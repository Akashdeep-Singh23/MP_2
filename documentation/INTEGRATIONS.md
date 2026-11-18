# INTEGRATIONS.md — External Integrations & Dependency Architecture

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** Implementation in progress; Supabase Data API readiness verified locally
**Authority Sources:** [PRD.md](../PRD.md) §11, §14, §15; [SRS.md](../SRS.md) §2.1, §5.4, §12  

---

## 1. External Integration Inventory

| Integration ID | System / Service | Provider | Communication Style | Integration Purpose |
|---|---|---|---|---|
| **INT-01** | **Supabase Auth (GoTrue)** | Hosted Supabase Inc. | HTTPS / REST (via SDK & JWT) | User identity management, registration, sign-in, JWT generation. |
| **INT-02** | **Supabase PostgreSQL** | Hosted Supabase Inc. | Supabase Data API (PostgREST) | Relational persistence for profiles, curated workouts, and history under user JWT + RLS. |
| **INT-03** | **Free Exercise DB** | Open Source (Yuhonas/GitHub) | File Download / Static JSON Ingestion | Source catalogue for normalized exercise metadata, instructions, and muscle tags. |

---

## 2. Integration Details

### 2.1 INT-01: Hosted Supabase Auth (GoTrue)
- **Business Justification:** Eliminates custom password storage, hashing vulnerabilities, and session-handling bugs; provides standard compliant JWTs.
- **Data Exchanged:**
  - *Outbound (Client to Supabase):* User email, password.
  - *Inbound (Supabase to Client):* User JWT access token, refresh token, Supabase User ID (`sub`).
  - *Account deletion:* FastAPI calls the JWT-protected `delete-account` Edge Function; its service key remains Supabase-managed.
- **Authentication & Secrets:**
  - Client utilizes `VITE_SUPABASE_ANON_KEY` (public, browser-safe).
  - The JWT-protected `delete-account` Edge Function uses the Supabase-managed service key for administrative deletion.
  - Backend validates bearer tokens with Supabase Auth `get_user(token)`; protected requests require Auth availability.
- **Failure Behavior & Fallbacks:**
  - If Supabase Auth is unreachable during sign-in: React client catches network exception and presents a user-friendly error: *"Authentication service temporarily unavailable. Please try again shortly."*
  - If token validation fails in FastAPI: Returns HTTP 401 `UNAUTHORIZED`.

---

### 2.2 INT-02: Hosted Supabase PostgreSQL
- **Business Justification:** Robust relational storage with ACID compliance, relational integrity constraints, and Row Level Security (RLS) enforcement.
- **Protocol & Connection:**
  - Supabase Python SDK Data API client; each API request uses the caller's verified JWT.
  - HTTPS Data API; the application server does not need direct Postgres credentials.
- **Data Exchanged:** Relational SQL queries and mutations across `profiles`, `exercises`, `workout_sessions`, `session_exercises`, `exercise_alternatives`, and `workout_history`.
- **Timeouts & Connection Pooling:**
  - Supabase SDK HTTP defaults apply; each user query forwards the caller's verified JWT for RLS.
  - `/api/health` performs a bounded read against the exercises table.
- **Failure Behavior:**
  - If the Supabase Data API is unreachable or rejects a query, FastAPI returns HTTP 503 `DATABASE_UNAVAILABLE` with a standard error envelope.

---

### 2.3 INT-03: Free Exercise DB Ingestion Pipeline
- **Business Justification:** Provides an open-source, standardized catalogue of exercises with instructions, muscle groups, and equipment tags, avoiding manual entry of hundreds of exercises.
- **Source Repository & Schema:**
  - Repository: `https://github.com/yuhonas/free-exercise-db`
  - License: Open Source (verified before import; attribution retained per **DATA-13**).
  - Ingestion Artifact: `exercises.json`
- **Data Transformation & Ingestion Workflow:**
  1. Script `scripts/ingest_catalogue.py` parses source JSON.
  2. Maps raw equipment values (e.g. `"dumbbell"`, `"body weight"`, `"cable"`) into the 10 controlled equipment vocabulary terms.
  3. Assigns difficulty (`Beginner`, `Intermediate`, `Advanced`).
  4. Exercises are initially inserted into PostgreSQL with `review_status = 'quarantined'`.
  5. A reviewer creates complete workout sessions with reviewed prescriptions and links approved source exercises.
  6. The validator checks integrity and coverage; it never approves records automatically.
- **Failure Behavior:**
  - Unrecognized equipment or malformed JSON records are logged and placed in the quarantine state; they are never exposed to the recommendation engine.

---

## 3. Secrets Management & Environment Isolation

| Secret Name | Location | Required In | Security Constraint |
|---|---|---|---|
| `SUPABASE_URL` | `.env` | Backend & Frontend | Public URL of the Supabase project. |
| `SUPABASE_ANON_KEY` | `.env` | Backend & Frontend | Safe for browser distribution; restricted by RLS. |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Edge Function secrets | **Function Only** | **CRITICAL:** Bypasses RLS; never copy to frontend or normal app runtime. Optional private ingestion tooling may use it locally. |
| `DATABASE_URL` | `backend/.env` | **Optional tooling only** | Needed only for direct-SQL catalogue validation and disposable integration tests. |

---

## 4. Diagnostics & Integration Health Check

The application provides an integrated health endpoint:
- **`GET /api/health`**
- **Diagnostic Behavior:**
  1. Verifies that FastAPI runtime is operational.
  2. Executes a lightweight `SELECT 1` query against the Supabase PostgreSQL database.
  3. Returns HTTP 200 with status `"healthy"`.
  4. If database connection fails, returns HTTP 503 with status `"unhealthy"` without leaking credentials or database connection strings.
