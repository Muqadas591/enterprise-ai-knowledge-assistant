from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Enterprise AI Knowledge Assistant API",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.APP_NAME,
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
    }