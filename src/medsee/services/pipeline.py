"""Multi-step reporting pipeline orchestrator."""

from collections.abc import Awaitable, Callable
from typing import Any

from medsee.core.config import Settings
from medsee.core.logging import get_logger
from medsee.llm.findings_agent import create_findings_agent, extract_findings
from medsee.llm.report_agent import assemble_report, create_report_agent
from medsee.models.enums import PipelineStep, StepStatus
from medsee.models.findings import FindingsResult
from medsee.models.intake import IntakeMetadata
from medsee.models.pipeline import PipelineResponse, StepStatusDetail
from medsee.models.report import ReportResult
from medsee.pipelines.router import get_pipeline_config
from medsee.services.validation import validate_findings

logger = get_logger(__name__)

FindingsExtractor = Callable[
    [bytes, str, IntakeMetadata, dict[str, Any]],
    Awaitable[FindingsResult],
]
ReportAssembler = Callable[[FindingsResult, IntakeMetadata], Awaitable[ReportResult]]


class PipelineService:
    """Orchestrates intake routing, chained LLM calls, and response assembly."""

    def __init__(
        self,
        settings: Settings,
        *,
        findings_extractor: FindingsExtractor | None = None,
        report_assembler: ReportAssembler | None = None,
    ) -> None:
        self._settings = settings
        self._findings_extractor = findings_extractor
        self._report_assembler = report_assembler
        self._findings_agent = None
        self._report_agent = None

    async def run(
        self,
        image_bytes: bytes,
        content_type: str,
        metadata: IntakeMetadata,
    ) -> PipelineResponse:
        modality_key, pipeline_config = get_pipeline_config(metadata.modality)
        step_statuses: list[StepStatusDetail] = []

        findings_result: FindingsResult | None = None
        report_result: ReportResult | None = None
        confidence: float | None = None

        # Call 1 — findings extraction
        try:
            raw_findings = await self._run_findings_extraction(
                image_bytes,
                content_type,
                metadata,
                pipeline_config,
            )
            validation = validate_findings(raw_findings)
            if not validation.ok:
                logger.warning(
                    "Findings validation failed for %s %s: %s",
                    metadata.modality,
                    metadata.body_part,
                    validation.error,
                )
                step_statuses.append(
                    StepStatusDetail(
                        step=PipelineStep.FINDINGS_EXTRACTION,
                        status=StepStatus.FAILED,
                        detail=validation.error,
                    )
                )
                step_statuses.append(
                    StepStatusDetail(
                        step=PipelineStep.REPORT_ASSEMBLY,
                        status=StepStatus.SKIPPED,
                        detail="Skipped because findings extraction failed validation",
                    )
                )
                return PipelineResponse(
                    findings=[],
                    report=None,
                    metadata=metadata,
                    pipeline_config=modality_key,
                    step_statuses=step_statuses,
                    confidence=None,
                )

            findings_result = validation.data
            assert findings_result is not None
            confidence = findings_result.overall_confidence
            step_statuses.append(
                StepStatusDetail(
                    step=PipelineStep.FINDINGS_EXTRACTION,
                    status=StepStatus.SUCCESS,
                )
            )
        except Exception as exc:
            logger.warning(
                "Findings extraction failed for %s %s: %s",
                metadata.modality,
                metadata.body_part,
                exc,
            )
            step_statuses.append(
                StepStatusDetail(
                    step=PipelineStep.FINDINGS_EXTRACTION,
                    status=StepStatus.FAILED,
                    detail=str(exc),
                )
            )
            step_statuses.append(
                StepStatusDetail(
                    step=PipelineStep.REPORT_ASSEMBLY,
                    status=StepStatus.SKIPPED,
                    detail="Skipped because findings extraction failed",
                )
            )
            return PipelineResponse(
                findings=[],
                report=None,
                metadata=metadata,
                pipeline_config=modality_key,
                step_statuses=step_statuses,
                confidence=None,
            )

        # Call 2 — report assembly (fed by validated Call 1 output)
        try:
            report_result = await self._run_report_assembly(findings_result, metadata)
            step_statuses.append(
                StepStatusDetail(
                    step=PipelineStep.REPORT_ASSEMBLY,
                    status=StepStatus.SUCCESS,
                )
            )
        except Exception as exc:
            logger.warning(
                "Report assembly failed for %s %s: %s",
                metadata.modality,
                metadata.body_part,
                exc,
            )
            step_statuses.append(
                StepStatusDetail(
                    step=PipelineStep.REPORT_ASSEMBLY,
                    status=StepStatus.FAILED,
                    detail=str(exc),
                )
            )

        return PipelineResponse(
            findings=findings_result.findings,
            report=report_result,
            metadata=metadata,
            pipeline_config=modality_key,
            step_statuses=step_statuses,
            confidence=confidence,
        )

    async def _run_findings_extraction(
        self,
        image_bytes: bytes,
        content_type: str,
        metadata: IntakeMetadata,
        pipeline_config: dict[str, Any],
    ) -> FindingsResult:
        if self._findings_extractor is not None:
            return await self._findings_extractor(
                image_bytes,
                content_type,
                metadata,
                pipeline_config,
            )
        if self._findings_agent is None:
            self._findings_agent = create_findings_agent(self._settings)
        return await extract_findings(
            self._findings_agent,
            image_bytes,
            content_type,
            metadata,
            pipeline_config,
        )

    async def _run_report_assembly(
        self,
        findings: FindingsResult,
        metadata: IntakeMetadata,
    ) -> ReportResult:
        if self._report_assembler is not None:
            return await self._report_assembler(findings, metadata)
        if self._report_agent is None:
            self._report_agent = create_report_agent(self._settings)
        return await assemble_report(self._report_agent, findings, metadata)
