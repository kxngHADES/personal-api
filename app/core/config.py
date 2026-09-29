import os

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class Settings:
    SUPABASE_URL: str = _require_env("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = _require_env("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = _require_env("SUPABASE_SERVICE_ROLE_KEY")
    DATABASE_URL: str = _require_env("DATABASE_URL")


settings = Settings()
