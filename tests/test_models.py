"""Smoke tests for Pydantic contracts."""

from medsee.models import (
    Finding,
    FindingsResult,
    IntakeMetadata,
    PipelineResponse,
    PipelineStep,
    ReportResult,
    StepStatus,
    StepStatusDetail,
    UrgencyFlag,
)


def test_models_import_and_validate() -> None:
    metadata = IntakeMetadata(
        modality="MRI",
        body_part="lumbar spine",
        clinical_context="back pain",
    )
    findings = FindingsResult(
        findings=[
            Finding(
                location="L5-S1",
                description="disc herniation",
                severity="severe",
                confidence_score=0.9,
            )
        ],
        overall_confidence=0.9,
    )
    report = ReportResult(
        impression="Severe disc herniation",
        recommendations=["Neurosurgical consult"],
        urgency=UrgencyFlag.CRITICAL,
    )
    response = PipelineResponse(
        findings=findings.findings,
        report=report,
        metadata=metadata,
        pipeline_config="MRI",
        step_statuses=[
            StepStatusDetail(step=PipelineStep.FINDINGS_EXTRACTION, status=StepStatus.SUCCESS),
            StepStatusDetail(step=PipelineStep.REPORT_ASSEMBLY, status=StepStatus.SUCCESS),
        ],
        confidence=0.9,
    )
    assert response.report.urgency == UrgencyFlag.CRITICAL
