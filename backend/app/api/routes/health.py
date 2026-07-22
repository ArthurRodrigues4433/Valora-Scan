from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.database import db

health_router = APIRouter(tags=["health"])


@health_router.get("/health/live")
async def health_live():
    return {"status": "ok"}


@health_router.get("/health/ready")
async def health_ready():
    try:
        with db.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
