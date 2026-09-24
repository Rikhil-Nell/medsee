"""Top-level API router."""

from fastapi import APIRouter

from medsee.api.routes import health, reports

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(reports.router)
