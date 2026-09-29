# Database connections (`app/core/database.py`)

This project talks to Supabase in two different ways, both wired up in
`app/core/database.py` and both driven by [`app/core/config.py`](./CORE.md):

1. **SQLAlchemy** — a direct Postgres connection for ORM models / raw SQL.
2. **Supabase client** — the `supabase-py` client for Auth, Storage, Realtime,
   and the PostgREST query builder.

Use whichever fits the task: reach for SQLAlchemy when you're doing
relational queries or need transactions/ORM models, and reach for the
Supabase client when you need Supabase-specific features (auth, storage,
row-level-security-aware `table()` calls, realtime, edge functions).

## SQLAlchemy engine and session

```python
from app.core.database import engine, SessionLocal, Base, get_db
```

- `engine` — a `sqlalchemy.Engine` created from `settings.DATABASE_URL`, with
  `pool_pre_ping=True` so dropped/idle connections are detected and
  transparently replaced instead of surfacing as errors.
- `SessionLocal` — a `sessionmaker` bound to `engine`. Construct sessions with
  `SessionLocal()`.
- `Base` — the `declarative_base()` all ORM models should inherit from.
- `get_db()` — a FastAPI dependency (generator) that yields a `Session` and
  guarantees it is closed afterwards, even if the request raises:

  ```python
  from fastapi import Depends
  from sqlalchemy import text
  from sqlalchemy.orm import Session

  from app.core.database import get_db

  @app.get("/health")
  def health_check(db: Session = Depends(get_db)):
      db.execute(text("SELECT 1"))
      return {"status": "ok"}
  ```

### `DATABASE_URL` format

Use the `psycopg2` SQLAlchemy dialect:

```
postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>
```

Get the connection string from your Supabase project: **Project Settings →
Database → Connection string**. Two host options matter:

- **Direct connection** (`db.<project-ref>.supabase.co:5432`) — simplest, but
  has a low connection limit. Fine for local dev and low-traffic APIs.
- **Connection pooler / PgBouncer** (`...pooler.supabase.com:6543`) —
  required in serverless/high-concurrency deployments where many short-lived
  connections would otherwise exhaust Postgres' connection limit.

If you see `could not translate host name "..." to address`, the host in
`DATABASE_URL` doesn't exist — double check it against the Supabase dashboard
and that `.env` (not just `.env.example`) has been filled in.

## Supabase client

```python
from app.core.database import get_supabase

@app.get("/example")
def example(supabase = Depends(get_supabase)):
    return supabase.table("some_table").select("*").execute()
```

`get_supabase()` builds a new `Client` using `settings.SUPABASE_URL` and
`settings.SUPABASE_SERVICE_ROLE_KEY` — i.e. it authenticates as the
**service role**, which bypasses Row Level Security. That's the correct
choice for trusted server-side code, but it means:

- Never forward this client's queries directly from unauthenticated,
  user-controlled input without your own authorization checks — RLS won't
  protect you here.
- Don't reuse this dependency for anything meant to run "as the end user"
  (e.g. respecting per-user RLS policies) — that would need a client built
  with `SUPABASE_ANON_KEY` plus the user's JWT instead.

## Testing

`tests/test_database.py` reloads `app.core.config` and `app.core.database`
under a fake, fully-populated environment (via `monkeypatch` +
`importlib.reload`) so the tests never open a real database connection or
call out to a real Supabase project:

- **Engine wiring** — asserts `engine.url` reflects `DATABASE_URL` exactly.
  Building an `Engine` does not open a connection, so this is safe to assert
  without a live database.
- **`get_db` yields and closes** — drives the generator with `next()`/
  `.close()` and, for the close path, substitutes a mocked `Session` so we
  can assert `close()` was actually called.
- **`get_supabase` returns a configured client** — `create_client()` only
  constructs the client object; it doesn't make a network call, so
  constructing it is safe in tests too.

Run the suite with:

```bash
uv run pytest tests/test_database.py -v
```
