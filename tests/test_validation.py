"""Tests for the findings validation gate."""

from medsee.models.findings import Finding, FindingsResult
from medsee.services.validation import validate_findings


def test_validate_findings_accepts_valid_result() -> None:
    outcome = validate_findings(
        FindingsResult(
            findings=[
                Finding(
                    location="C5-C6",
                    description="Mild stenosis",
                    severity="mild",
                    confidence_score=0.7,
                )
            ]
        )
    )
    assert outcome.ok is True
    assert outcome.data is not None
    assert len(outcome.data.findings) == 1


def test_validate_findings_rejects_empty_findings() -> None:
    outcome = validate_findings({"findings": []})
    assert outcome.ok is False
    assert outcome.error is not None


def test_validate_findings_rejects_malformed_payload() -> None:
    outcome = validate_findings({"findings": [{"location": "L1", "confidence_score": 2.0}]})
    assert outcome.ok is False
    assert outcome.error is not None
