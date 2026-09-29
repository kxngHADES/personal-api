from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from supabase import Client

from app.core.database import get_db, get_supabase

app = FastAPI(
    title="Personal API",
    description="Ndaedzo Rudzani \"Brandon\" Personal API",
    version="0.0.1"
)

@app.get("/")
def read_root():
    return {"message": "Hello from Personal API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db), supabase: Client = Depends(get_supabase)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {exc}") from exc

    return {"status": "ok", "database": "connected", "supabase": "connected"}

@app.get("/me")
def get_me():
    return {
        "Full Name": "Ndaedzo Rudzani Brandon Mudau",
        "role": "Software Engineer, Business Analyst, DevOps engineer",
        "location": "Centurion, South Africa",
        "github": "https://"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)