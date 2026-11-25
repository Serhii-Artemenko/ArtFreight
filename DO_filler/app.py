import logging

import psycopg
from fastapi import FastAPI, HTTPException

from database import get_connection


app = FastAPI(title="ArtFreight API")
logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/database")
def database_health():
    try:
        with get_connection() as connection:
            result = connection.execute("SELECT 1").fetchone()

    except (psycopg.Error, RuntimeError):
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable.",
        ) from None

    return {
        "status": "ok",
        "database_connected": result == (1,),
    }