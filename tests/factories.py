"""Shared test data factories."""

from medsee.models.enums import UrgencyFlag
from medsee.models.findings import Finding, FindingsResult
from medsee.models.report import ReportResult

SAMPLE_FINDINGS = FindingsResult(
    findings=[
        Finding(
            location="L4-L5",
            description="Posterior disc bulge with mild canal narrowing",
            severity="moderate",
            confidence_score=0.87,
        )
    ],
    summary="Single moderate lumbar finding",
    overall_confidence=0.87,
)

SAMPLE_REPORT = ReportResult(
    impression="Moderate L4-L5 disc bulge without acute nerve compression.",
    recommendations=["Conservative management", "Follow-up if symptoms worsen"],
    urgency=UrgencyFlag.IMPORTANT,
)

SAMPLE_METADATA_JSON = (
    '{"modality":"MRI","body_part":"lumbar spine","clinical_context":"chronic low back pain"}'
)

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)
