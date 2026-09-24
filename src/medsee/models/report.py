"""Report assembly models produced by Call 2."""

from pydantic import BaseModel, Field

from medsee.models.enums import UrgencyFlag


class ReportResult(BaseModel):
    """Structured radiology report assembled from validated findings."""

    impression: str
    recommendations: list[str] = Field(min_length=1)
    urgency: UrgencyFlag
