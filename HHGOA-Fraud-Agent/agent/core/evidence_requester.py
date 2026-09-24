"""Controlled Evidence-Request Mechanism for Fraud Investigation Agent.

Simulates responses for additional evidence gathering (e.g. customer validation, step-up auth, analyst info)
for hackathon evaluation. Clearly labels simulated/assumed responses.
"""

from typing import Dict, Any, Optional
from agent.schemas.evidence_schema import EvidenceRequest, EvidenceRequestTypeEnum


class EvidenceRequester:
    """Manages creation and simulation of additional evidence requests."""

    @classmethod
    def create_evidence_request(
        cls,
        request_type: EvidenceRequestTypeEnum,
        step: int,
        context: Dict[str, Any],
    ) -> EvidenceRequest:
        """
        Creates a structured evidence request with an explicit assumed test response.
        Note: Clearly marked as SIMULATED / TEST EVIDENCE for hackathon evaluation.
        """
        trigger_type = context.get("trigger_type", "")
        amt = float(context.get("amount", 0.0))

        if request_type == EvidenceRequestTypeEnum.CUSTOMER_VALIDATION:
            if trigger_type == "customer_report":
                assumed_resp = (
                    "SIMULATED TEST EVIDENCE: Customer confirmed dispute, stating they did not make this "
                    f"${amt:.2f} purchase and remained in possession of the card."
                )
            elif amt > 500.0:
                assumed_resp = (
                    f"SIMULATED TEST EVIDENCE: Customer contacted via SMS; denies authorizing ${amt:.2f} transaction."
                )
            else:
                assumed_resp = (
                    f"SIMULATED TEST EVIDENCE: Customer contacted; confirms they recognized the transaction as legitimate."
                )

        elif request_type == EvidenceRequestTypeEnum.STEP_UP_AUTH:
            assumed_resp = (
                "SIMULATED TEST EVIDENCE: Step-up one-time authentication passcode was dispatched to mobile device on file; verification failed (timed out)."
            )

        elif request_type == EvidenceRequestTypeEnum.ANALYST_INFO:
            assumed_resp = (
                "SIMULATED TEST EVIDENCE: Fraud analyst confirms device fingerprint is associated with an active multi-card fraud syndicate investigation."
            )

        else:
            assumed_resp = "SIMULATED TEST EVIDENCE: Additional transaction telemetry retrieved."

        return EvidenceRequest(
            type=request_type,
            asked_after_step=step,
            assumed_response=assumed_resp,
        )
