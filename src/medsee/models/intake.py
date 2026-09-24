"""Intake request metadata models."""

from pydantic import BaseModel, Field


class IntakeMetadata(BaseModel):
    """Metadata submitted alongside an imaging study upload."""

    modality: str = Field(description="Imaging modality, e.g. MRI, CT, XRAY")
    body_part: str = Field(description="Anatomical region under study")
    clinical_context: str = Field(description="Relevant clinical history and indication")
