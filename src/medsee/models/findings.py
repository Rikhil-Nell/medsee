"""Structured findings models produced by Call 1."""

from pydantic import BaseModel, Field


class FindingRegion(BaseModel):
    """Approximate normalized bounding box on the source image (0–1)."""

    x: float = Field(ge=0.0, le=1.0, description="Left edge")
    y: float = Field(ge=0.0, le=1.0, description="Top edge")
    width: float = Field(ge=0.0, le=1.0)
    height: float = Field(ge=0.0, le=1.0)


class Finding(BaseModel):
    """Single imaging finding with location, severity, and confidence."""

    location: str
    description: str
    severity: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    region: FindingRegion | None = None


class FindingsResult(BaseModel):
    """Validated output from the findings extraction LLM call."""

    findings: list[Finding]
    summary: str | None = None
    overall_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
