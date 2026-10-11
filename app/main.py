from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, conversations, documents, health, qa, retrieval
from app.core.config import settings
from app.core.logging import configure_logging
from app.observability.middleware import (
    RateLimitMiddleware,
    RequestObservabilityMiddleware,
)
from app.api.routes import document_sources
from app.api.routes import feedback

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=("Production-oriented API for an enterprise AI knowledge assistant."),
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestObservabilityMiddleware)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Enterprise AI Knowledge Assistant API",
        "docs": "/docs",
    }


app.include_router(
    auth.router,
)

app.include_router(conversations.router)

app.include_router(
    documents.router,
    prefix="/api/v1",
)
app.include_router(
    document_sources.router,
    prefix="/api/v1",
)

app.include_router(
    health.router,
    prefix="/api/v1",
)
app.include_router(
    feedback.router,
    prefix="/api/v1",
)
app.include_router(retrieval.router)

app.include_router(qa.router)
