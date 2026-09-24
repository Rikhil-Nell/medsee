"""Shared enumerations for the reporting pipeline."""

from enum import StrEnum


class UrgencyFlag(StrEnum):
    CRITICAL = "CRITICAL"
    IMPORTANT = "IMPORTANT"
    ROUTINE = "ROUTINE"


class StepStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStep(StrEnum):
    FINDINGS_EXTRACTION = "findings_extraction"
    REPORT_ASSEMBLY = "report_assembly"
