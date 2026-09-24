"""FastAPI dependency providers."""

from medsee.core.config import Settings, get_settings
from medsee.services.pipeline import PipelineService


def get_settings_dep() -> Settings:
    return get_settings()


def get_pipeline_service() -> PipelineService:
    return PipelineService(get_settings())
