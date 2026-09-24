"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from medsee.api.router import api_router
from medsee.core.config import get_settings
from medsee.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Starting medsee service (env=%s)", settings.app_env)
    yield
    logger.info("Shutting down medsee service")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Medsee Reporting Pipeline",
        description="POC for multi-step radiology reporting with chained LLM calls.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"service": "medsee", "env": settings.app_env}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "medsee.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.app_env == "development",
    )
