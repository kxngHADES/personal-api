# Core module (`app/core`)

The `app/core` package holds the two pieces of application-wide plumbing every
route depends on:

| File                    | Responsibility                                               |
| ----------------------- | -------------------------------------------------------------- |
| `app/core/config.py`    | Loads and validates environment configuration (`settings`).    |
| `app/core/database.py`  | Builds the Postgres/SQLAlchemy connection and the Supabase client. |

See [`DATABASE.md`](./DATABASE.md) for details on the database connections
specifically.

## Configuration (`config.py`)

`config.py` loads variables from a `.env` file (via `python-dotenv`) and
exposes them through a module-level `settings` singleton:

```python
from app.core.config import settings

settings.SUPABASE_URL
settings.SUPABASE_ANON_KEY
settings.SUPABASE_SERVICE_ROLE_KEY
settings.DATABASE_URL
```

### Required environment variables

| Variable                     | Purpose                                                               |
| ----------------------------- | ---------------------------------------------------------------------- |
| `SUPABASE_URL`                | Your Supabase project URL (`https://<project-ref>.supabase.co`).       |
| `SUPABASE_ANON_KEY`           | Public anon key, safe for client-facing use under RLS.                 |
| `SUPABASE_SERVICE_ROLE_KEY`   | Secret service-role key. Bypasses RLS — server-side use only, never expose it. |
| `DATABASE_URL`                | SQLAlchemy connection string to the Supabase Postgres database.        |

Copy `.env.example` to `.env` and fill in real values before running the app.
`.env` is git-ignored; only `.env.example` (with placeholder values) is committed.

### Fail-fast validation

Every variable is required. If one is missing or blank, importing
`app.core.config` raises a `RuntimeError` immediately, naming the missing
variable:

```
RuntimeError: Missing required environment variable: DATABASE_URL
```

This means a misconfigured deployment fails at startup, not on the first
request that happens to touch the database.

## Using core in routes

FastAPI routes pull the database session and Supabase client in via
dependency injection, never by importing `settings` or constructing clients
directly:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from supabase import Client

from app.core.database import get_db, get_supabase

@app.get("/example")
def example(db: Session = Depends(get_db), supabase: Client = Depends(get_supabase)):
    ...
```

## Tests

`tests/test_config.py` and `tests/test_database.py` cover this package. Because
`settings` and the database engine/client are built once at import time, the
tests reload the modules under controlled environment variables (via
`monkeypatch` + `importlib.reload`) to exercise both the "happy path" and the
missing-variable failure path without ever touching a real database or
Supabase project. Run them with:

```bash
uv run pytest
```
