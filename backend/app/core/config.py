from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Personalized AI Fitness System"
    APP_ENV: str = "development"
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,testserver"

    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    DATABASE_URL: str = ""

    DEFAULT_TOP_K: int = 5
    DURATION_WARNING_THRESHOLD_MINUTES: int = 10

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def trusted_hosts(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV.strip().lower() in {"development", "local", "test"}

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"), extra="allow"
    )

    def require_supabase_auth(self) -> None:
        if (
            not self.SUPABASE_URL
            or not self.SUPABASE_ANON_KEY
            or "<" in self.SUPABASE_URL + self.SUPABASE_ANON_KEY
            or "placeholder" in (self.SUPABASE_URL + self.SUPABASE_ANON_KEY).lower()
            or "YOUR_" in self.SUPABASE_URL + self.SUPABASE_ANON_KEY
        ):
            raise RuntimeError("Supabase Auth is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")

    def require_service_role(self) -> None:
        self.require_supabase_auth()
        if (
            not self.SUPABASE_SERVICE_ROLE_KEY
            or "YOUR_" in self.SUPABASE_SERVICE_ROLE_KEY
            or "placeholder" in self.SUPABASE_SERVICE_ROLE_KEY.lower()
        ):
            raise RuntimeError("Supabase account deletion is not configured. Set SUPABASE_SERVICE_ROLE_KEY.")

    def require_database(self) -> None:
        if (
            not self.DATABASE_URL
            or not self.DATABASE_URL.startswith(("postgresql://", "postgres://"))
            or "YOUR_" in self.DATABASE_URL
            or "<" in self.DATABASE_URL
            or "placeholder" in self.DATABASE_URL.lower()
        ):
            raise RuntimeError("Supabase Postgres is not configured. Set DATABASE_URL for direct SQL tooling.")

settings = Settings()
