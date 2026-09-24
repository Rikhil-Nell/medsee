"""Unified pipeline response envelope."""

from pydantic import BaseModel, Field

from medsee.models.enums import PipelineStep, StepStatus
from medsee.models.findings import Finding
from medsee.models.intake import IntakeMetadata
from medsee.models.report import ReportResult


class StepStatusDetail(BaseModel):
    """Status of an individual pipeline step."""

    step: PipelineStep
    status: StepStatus
    detail: str | None = None


class PipelineResponse(BaseModel):
    """Frontend-ready response from the multi-step reporting pipeline."""

    findings: list[Finding]
    report: ReportResult | None
    metadata: IntakeMetadata
    pipeline_config: str
    step_statuses: list[StepStatusDetail]
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Overall pipeline confidence indicator",
    )
