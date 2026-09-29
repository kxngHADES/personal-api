# Personal API
-----

## Build and Run commands for `Render`

**Build Command:**
```bash
pip install uv && uv sync --frozen --no-dev
```

**Start Command:**
```bash
uv run uvicorn main:app --host 0.0.0.0 --port $PORT
```