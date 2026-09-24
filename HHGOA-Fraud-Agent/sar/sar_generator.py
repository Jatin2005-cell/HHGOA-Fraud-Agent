"""SAR Generator: Evaluates policy conditions and constructs validated regulatory filings."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .sar_narrative import SARNarrativeBuilder
from .sar_validator import SARValidator, SARValidationResult


class GeneratedSAR(BaseModel):
    file: bool = False
    reason: str = ""
    narrative: str = ""
    subjects: List[str] = Field(default_factory=list)
    total_amount_usd: float = 0.0
    activity_dates: List[str] = Field(default_factory=list)
    status: str = "NOT_REQUIRED"  # NOT_REQUIRED | PENDING | GENERATED | REVIEW_REQUIRED
    validation_errors: List[str] = Field(default_factory=list)


class SARGenerator:
    """Evaluates case evidence against FinCEN and Bank Fraud Policy standards to construct SAR records."""

    @classmethod
    def generate_for_case(cls, case_data: Dict[str, Any]) -> GeneratedSAR:
        """Generates a complete, validated SAR record for a case."""
        exposure = float(case_data.get("exposure_usd", 0.0))
        pattern = str(case_data.get("fraud_pattern", case_data.get("pattern", "none")))
        device_profiles = case_data.get("connected_device_profiles", [])
        connected_cards = case_data.get("connected_card_ids", [])
        verdict = str(case_data.get("verdict", "uncertain"))

        # Determine if SAR is mandated:
        # 1. Exposure >= $1,000 AND confirmed/suspected fraud
        # 2. Shared device ring / syndicate
        # 3. Policy R6 or R9 triggered
        # 4. Explicitly flagged in final_actions
        final_actions = case_data.get("final_next_best_action", [])
        has_file_report = any(
            a.get("action") == "FILE_REPORT" for a in final_actions if isinstance(a, dict)
        )

        should_file = has_file_report or (
            verdict == "fraud" and (exposure >= 1000.0 or len(device_profiles) > 0 or pattern in ["undocumented", "card_testing"])
        )

        if not should_file:
            return GeneratedSAR(
                file=False,
                reason="Regulatory threshold not met; exposure below $1,000 and no multi-card syndicate detected.",
                narrative="",
                subjects=[],
                total_amount_usd=0.0,
                activity_dates=[],
                status="NOT_REQUIRED",
            )

        cid = str(case_data.get("customer_id", ""))
        card_id = str(case_data.get("card_id", ""))
        flagged_txn = str(case_data.get("flagged_txn_id", ""))
        affected_txns = case_data.get("affected_txn_ids", [flagged_txn] if flagged_txn else [])

        date_str = str(case_data.get("created_at", case_data.get("opened_at", "2016-12-01")))[:10]
        activity_dates = [date_str, date_str]

        subjects = [s for s in [cid, card_id] + connected_cards + device_profiles if s]

        policy_reason = "R2/R6: Confirmed unauthorized activity exceeding reporting threshold or linked to multi-card syndicate"
        if pattern == "undocumented":
            policy_reason = "R9: Coordinated novel fraud pattern affecting payment infrastructure"

        narrative = SARNarrativeBuilder.build_narrative(
            case_id=str(case_data.get("case_id", "")),
            customer_id=cid,
            card_id=card_id,
            flagged_txn_id=flagged_txn,
            affected_txn_ids=affected_txns,
            total_amount_usd=exposure,
            activity_dates=activity_dates,
            pattern=pattern,
            device_profiles=device_profiles,
            connected_cards=connected_cards,
            policy_reason=policy_reason,
        )

        sar_payload = {
            "file": True,
            "reason": policy_reason,
            "narrative": narrative,
            "subjects": subjects,
            "total_amount_usd": exposure,
            "activity_dates": activity_dates,
        }

        # Validate
        val_res = SARValidator.validate_sar(sar_payload, case_data)

        return GeneratedSAR(
            file=True,
            reason=policy_reason,
            narrative=narrative,
            subjects=subjects,
            total_amount_usd=exposure,
            activity_dates=activity_dates,
            status=val_res.status,
            validation_errors=val_res.errors,
        )
