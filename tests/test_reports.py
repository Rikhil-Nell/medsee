"""Integration tests for POST /reports."""

from typing import Any

import pytest
from httpx import AsyncClient

from medsee.api.deps import get_pipeline_service
from medsee.core.config import Settings
from medsee.main import app
from medsee.models.enums import PipelineStep, StepStatus, UrgencyFlag
from medsee.models.findings import FindingsResult
from medsee.models.intake import IntakeMetadata
from medsee.models.report import ReportResult
from medsee.services.pipeline import PipelineService

from .factories import MINIMAL_PNG, SAMPLE_FINDINGS, SAMPLE_METADATA_JSON, SAMPLE_REPORT


def _multipart(metadata: str = SAMPLE_METADATA_JSON) -> dict[str, Any]:
    return {
        "metadata": (None, metadata),
        "image": ("scan.png", MINIMAL_PNG, "image/png"),
    }


@pytest.fixture
def override_pipeline(app_service: PipelineService):
    app.dependency_overrides[get_pipeline_service] = lambda: app_service
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def app_service() -> PipelineService:
    async def extract_findings(
        _image_bytes: bytes,
        _content_type: str,
        _metadata: IntakeMetadata,
        _pipeline_config: dict,
    ) -> FindingsResult:
        return SAMPLE_FINDINGS

    async def assemble_report(
        findings: FindingsResult,
        _metadata: IntakeMetadata,
    ) -> ReportResult:
        assert findings == SAMPLE_FINDINGS
        return SAMPLE_REPORT

    return PipelineService(
        Settings(),
        findings_extractor=extract_findings,
        report_assembler=assemble_report,
    )


@pytest.mark.asyncio
async def test_create_report_happy_path(
    client: AsyncClient,
    override_pipeline,
) -> None:
    response = await client.post("/reports", files=_multipart())
    assert response.status_code == 200
    body = response.json()

    assert body["pipeline_config"] == "MRI"
    assert len(body["findings"]) == 1
    assert body["report"]["urgency"] == UrgencyFlag.IMPORTANT
    assert body["confidence"] == 0.87
    assert all(step["status"] == StepStatus.SUCCESS for step in body["step_statuses"])


@pytest.mark.asyncio
async def test_create_report_invalid_modality(client: AsyncClient) -> None:
    metadata = '{"modality":"PET","body_part":"brain","clinical_context":"rule out malignancy"}'
    response = await client.post("/reports", files=_multipart(metadata))
    assert response.status_code == 422
    assert "Unsupported modality" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_report_invalid_metadata(client: AsyncClient) -> None:
    response = await client.post(
        "/reports",
        files=_multipart('{"modality":"MRI","body_part":"spine"}'),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("modality", "expected_config"),
    [("MRI", "MRI"), ("CT", "CT"), ("XRAY", "XRAY"), ("mri", "MRI")],
)
async def test_create_report_modality_routing(
    client: AsyncClient,
    modality: str,
    expected_config: str,
) -> None:
    async def extract_findings(
        _image_bytes: bytes,
        _content_type: str,
        metadata: IntakeMetadata,
        _pipeline_config: dict,
    ) -> FindingsResult:
        assert metadata.modality.upper() == expected_config
        return SAMPLE_FINDINGS

    async def assemble_report(
        _findings: FindingsResult,
        _metadata: IntakeMetadata,
    ) -> ReportResult:
        return SAMPLE_REPORT

    service = PipelineService(
        Settings(),
        findings_extractor=extract_findings,
        report_assembler=assemble_report,
    )
    app.dependency_overrides[get_pipeline_service] = lambda: service

    metadata = f'{{"modality":"{modality}","body_part":"chest","clinical_context":"cough"}}'
    response = await client.post("/reports", files=_multipart(metadata))
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["pipeline_config"] == expected_config


@pytest.mark.asyncio
async def test_create_report_malformed_call1_returns_degraded_response(
    client: AsyncClient,
) -> None:
    async def extract_findings(
        _image_bytes: bytes,
        _content_type: str,
        _metadata: IntakeMetadata,
        _pipeline_config: dict,
    ) -> FindingsResult:
        return FindingsResult(findings=[])

    service = PipelineService(Settings(), findings_extractor=extract_findings)
    app.dependency_overrides[get_pipeline_service] = lambda: service

    response = await client.post("/reports", files=_multipart())
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["findings"] == []
    assert body["report"] is None

    statuses = {step["step"]: step["status"] for step in body["step_statuses"]}
    assert statuses[PipelineStep.FINDINGS_EXTRACTION] == StepStatus.FAILED
    assert statuses[PipelineStep.REPORT_ASSEMBLY] == StepStatus.SKIPPED


@pytest.mark.asyncio
async def test_create_report_call2_failure_preserves_findings(
    client: AsyncClient,
) -> None:
    async def extract_findings(
        _image_bytes: bytes,
        _content_type: str,
        _metadata: IntakeMetadata,
        _pipeline_config: dict,
    ) -> FindingsResult:
        return SAMPLE_FINDINGS

    async def failing_report(
        _findings: FindingsResult,
        _metadata: IntakeMetadata,
    ) -> ReportResult:
        raise RuntimeError("LLM returned malformed report output")

    service = PipelineService(
        Settings(),
        findings_extractor=extract_findings,
        report_assembler=failing_report,
    )
    app.dependency_overrides[get_pipeline_service] = lambda: service

    response = await client.post("/reports", files=_multipart())
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body["findings"]) == 1
    assert body["report"] is None

    statuses = {step["step"]: step["status"] for step in body["step_statuses"]}
    assert statuses[PipelineStep.FINDINGS_EXTRACTION] == StepStatus.SUCCESS
    assert statuses[PipelineStep.REPORT_ASSEMBLY] == StepStatus.FAILED
