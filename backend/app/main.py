import uuid
import logging
import math
import time
import threading
from collections import OrderedDict, deque
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, request_id_ctx_var
from app.api.api_router import api_router
from app.services.database import DatabaseUnavailable
from contextlib import asynccontextmanager

setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=False,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    lifespan=lifespan,
)

# Pure ASGI Request ID Middleware (API-02, API-05 - Avoids BaseHTTPMiddleware deadlock)
class RequestIdMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        candidate = headers.get(b"x-request-id", b"").decode("utf-8", errors="ignore")
        try:
            req_id = str(uuid.UUID(candidate))
        except (ValueError, AttributeError):
            req_id = str(uuid.uuid4())
        request_id_ctx_var.set(req_id)

        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = req_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                res_headers = list(message.get("headers", []))
                res_headers.append((b"x-request-id", req_id.encode("utf-8")))
                message["headers"] = res_headers
            await send(message)

        await self.app(scope, receive, send_wrapper)

app.add_middleware(RequestIdMiddleware)


class SecurityHeadersMiddleware:
    """Add browser security headers without trusting client supplied values."""

    def __init__(self, inner_app):
        self.inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.inner_app(scope, receive, send)
            return

        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() not in {
                        b"x-content-type-options", b"x-frame-options", b"referrer-policy",
                        b"permissions-policy", b"content-security-policy", b"cache-control",
                        b"strict-transport-security",
                    }
                ]
                headers.extend([
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                ])
                path = scope.get("path", "")
                if path.startswith("/api/"):
                    headers.extend([
                        (b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"),
                        (b"cache-control", b"no-store"),
                    ])
                if scope.get("scheme") == "https":
                    headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
                message["headers"] = headers
            await send(message)

        await self.inner_app(scope, receive, send_with_security_headers)


class RateLimitMiddleware:
    """Bound request bursts per peer IP; production multi instance limits belong at the edge too."""

    def __init__(self, inner_app, window_seconds=60, max_clients=10000):
        self.inner_app = inner_app
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self.requests = OrderedDict()
        self.lock = threading.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") == "OPTIONS":
            await self.inner_app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith("/api/recommendations"):
            limit = 30
            bucket = "recommendations"
        elif path.startswith("/api/account"):
            limit = 5
            bucket = "account"
        else:
            limit = 120
            bucket = "general"

        peer = scope.get("client")
        client_ip = peer[0] if peer else "unknown"
        key = (client_ip, bucket)
        now = time.monotonic()
        retry_after = 0
        with self.lock:
            hits = self.requests.get(key)
            if hits is None:
                hits = deque()
                self.requests[key] = hits
            while hits and now - hits[0] >= self.window_seconds:
                hits.popleft()
            self.requests.move_to_end(key)
            if len(hits) >= limit:
                retry_after = max(1, math.ceil(self.window_seconds - (now - hits[0])))
            else:
                hits.append(now)
            if len(self.requests) > self.max_clients:
                self.requests.popitem(last=False)

        if retry_after:
            response = JSONResponse(
                status_code=429,
                content={"error": {"code": "RATE_LIMITED", "message": "Too many requests. Wait before trying again."}},
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return

        await self.inner_app(scope, receive, send)


app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

# Browser API access uses bearer tokens, not cookies. Keep methods and headers explicit.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
    expose_headers=["X-Request-ID", "Retry-After"],
)

# Standard Error Envelope Exception Handlers (API-02, NFR-SEC-07)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    detail = exc.detail

    if isinstance(detail, dict):
        code = detail.get("code", "ERROR")
        message = detail.get("message", "An error occurred.")
        details = detail.get("details", None)
    else:
        code = "HTTP_ERROR"
        message = str(detail)
        details = None

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": req_id
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    errors = []
    for err in exc.errors():
        safe_err = {
            "field": ".".join(str(loc) for loc in err.get("loc", [])),
            "msg": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error")
        }
        errors.append(safe_err)

    first_msg = errors[0]["msg"] if errors else "Validation failed"
    first_field = errors[0]["field"] if errors else "unknown"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"Validation failed: {first_msg}",
                "details": {"field": first_field, "errors": errors},
                "request_id": req_id
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    if settings.is_development:
        logger.error("Unhandled exception (%s)", type(exc).__name__, exc_info=True)
    else:
        logger.error("Unhandled exception (%s)", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": None,
                "request_id": req_id
            }
        }
    )


@app.exception_handler(DatabaseUnavailable)
@app.exception_handler(OSError)
@app.exception_handler(TimeoutError)
async def database_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    if settings.is_development:
        logger.error("Database service unavailable (%s)", type(exc).__name__, exc_info=True)
    else:
        logger.error("Database service unavailable (%s)", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": "DATABASE_UNAVAILABLE",
                "message": "The database is temporarily unavailable.",
                "details": None,
                "request_id": req_id,
            }
        },
    )

# Mount API routes
app.include_router(api_router, prefix="/api")
