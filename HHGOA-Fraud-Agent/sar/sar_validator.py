"""SAR Validator: Enforces strict legal completeness, evidence consistency, and policy adherence."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SARValidationResult(BaseModel):
    is_valid: bool
    status: str  # GENERATED | REVIEW_REQUIRED | NOT_REQUIRED
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class SARValidator:
    """Validates generated SAR records against FinCEN legal standards and Bank Policy."""

    @classmethod
    def validate_sar(cls, sar_data: Dict[str, Any], case_context: Dict[str, Any]) -> SARValidationResult:
        errors = []
        warnings = []

        is_filing = bool(sar_data.get("file", False))
        if not is_filing:
            return SARValidationResult(
                is_valid=True,
                status="NOT_REQUIRED",
                errors=[],
                warnings=[],
            )

        # 1. Reason validation
        reason = str(sar_data.get("reason", "")).strip()
        if not reason:
            errors.append("SAR reason is missing.")
        elif not any(r in reason for r in ["R2", "R6", "R9", "1000", "syndicate"]):
            warnings.append("SAR reason does not cite standard policy rule (R2, R6, R9).")

        # 2. Narrative completeness
        narrative = str(sar_data.get("narrative", "")).strip()
        if not narrative:
            errors.append("SAR narrative is empty.")
        elif len(narrative.split()) < 40:
            errors.append("SAR narrative fails minimum length requirement (must be >= 40 words).")

        # 3. Subjects list
        subjects = sar_data.get("subjects", [])
        if not subjects or len(subjects) == 0:
            errors.append("SAR subjects list cannot be empty when filing is mandated.")

        # 4. Amount consistency
        total_amount = float(sar_data.get("total_amount_usd", 0.0))
        case_exposure = float(case_context.get("exposure_usd", 0.0))
        if total_amount < 0.0:
            errors.append("SAR total_amount_usd cannot be negative.")
        if case_exposure > 0 and abs(total_amount - case_exposure) > 1.0:
            errors.append(f"SAR amount (${total_amount:.2f}) diverges from case exposure (${case_exposure:.2f}).")

        # 5. Activity dates
        dates = sar_data.get("activity_dates", [])
        if not dates or len(dates) == 0:
            errors.append("SAR activity_dates cannot be empty when filing is required.")

        status = "GENERATED" if len(errors) == 0 else "REVIEW_REQUIRED"
        return SARValidationResult(
            is_valid=(len(errors) == 0),
            status=status,
            errors=errors,
            warnings=warnings,
        )
