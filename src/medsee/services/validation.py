"""Validation gate between Call 1 and Call 2."""

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from medsee.models.findings import FindingsResult


@dataclass(frozen=True)
class FindingsValidationOutcome:
    """Result of validating findings extraction output."""

    ok: bool
    data: FindingsResult | None = None
    error: str | None = None


def validate_findings(raw: Any) -> FindingsValidationOutcome:
    """Parse and validate Call 1 output before feeding it to Call 2."""
    try:
        if isinstance(raw, FindingsResult):
            validated = raw
        else:
            validated = FindingsResult.model_validate(raw)

        if not validated.findings:
            return FindingsValidationOutcome(
                ok=False,
                error="Findings extraction returned an empty findings list",
            )

        for finding in validated.findings:
            if not finding.location.strip() or not finding.description.strip():
                return FindingsValidationOutcome(
                    ok=False,
                    error="Each finding must include non-empty location and description",
                )

        return FindingsValidationOutcome(ok=True, data=validated)
    except ValidationError as exc:
        return FindingsValidationOutcome(ok=False, error=str(exc))
