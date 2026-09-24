"""Report generation endpoints."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from medsee.api.deps import get_pipeline_service
from medsee.models.intake import IntakeMetadata
from medsee.models.pipeline import PipelineResponse
from medsee.pipelines.router import InvalidModalityError, get_pipeline_config
from medsee.services.pipeline import PipelineService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=PipelineResponse)
async def create_report(
    image: Annotated[UploadFile, File(description="Medical image to analyze")],
    metadata: Annotated[str, Form(description="JSON metadata for the study")],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> PipelineResponse:
    """Accept an image upload with metadata and run the reporting pipeline."""
    try:
        metadata_dict = json.loads(metadata)
        intake_metadata = IntakeMetadata.model_validate(metadata_dict)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid metadata: {exc}") from exc

    try:
        get_pipeline_config(intake_metadata.modality)
    except InvalidModalityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=422, detail="Image file is empty")

    content_type = image.content_type or "application/octet-stream"
    return await pipeline_service.run(image_bytes, content_type, intake_metadata)
