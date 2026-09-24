"""Uncertainty Engine for Fraud Investigation.

Evaluates evidence completeness, conflicting signals, and determines if additional
evidence is required before concluding an investigation.
"""

from typing import Any, Dict, List
from agent.schemas.evidence_schema import EvidenceRequestTypeEnum


class UncertaintyManager:
    """Evaluates whether current evidence warrants an evidence request under Policy R1/R4."""

    @classmethod
    def evaluate_uncertainty(
        cls,
        trigger_type: str,
        fraud_probability: float,
        verdict: str,
        supporting_evidence: List[str],
        contradicting_evidence: List[str],
        evidence_requests_already_made: int = 0,
    ) -> Dict[str, Any]:
        """
        Determines:
            status: SUFFICIENT | INSUFFICIENT | CONFLICTING
            reason: str
            missing_evidence: List[str]
            recommended_evidence: List[EvidenceRequestTypeEnum]
        """
        # If evidence was already requested and simulated response received, evidence is sufficient
        if evidence_requests_already_made > 0:
            return {
                "status": "SUFFICIENT",
                "reason": "Follow-up verification completed; sufficient evidence to finalize actions under policy.",
                "missing_evidence": [],
                "recommended_evidence": [],
            }

        # Clear high-confidence fraud (e.g. card testing sequence confirmed or multi-card shared device ring)
        if fraud_probability >= 0.85 and len(supporting_evidence) >= 2:
            return {
                "status": "SUFFICIENT",
                "reason": f"Fraud pattern definitively confirmed by {len(supporting_evidence)} independent graph signals (prob {fraud_probability:.2f}).",
                "missing_evidence": [],
                "recommended_evidence": [],
            }

        # Clear legitimate false-alarm (e.g. established billing region or known recurring habit)
        if fraud_probability <= 0.15:
            return {
                "status": "SUFFICIENT",
                "reason": f"Activity consistent with cardholder normal profile (prob {fraud_probability:.2f}); false positive alert.",
                "missing_evidence": [],
                "recommended_evidence": [],
            }

        # Conflicting evidence
        if supporting_evidence and contradicting_evidence:
            return {
                "status": "CONFLICTING",
                "reason": "Conflicting evidence observed between risk alert and normal customer spend baseline. Policy R1 mandates customer verification.",
                "missing_evidence": ["Cardholder authorization confirmation"],
                "recommended_evidence": [EvidenceRequestTypeEnum.CUSTOMER_VALIDATION],
            }

        # Policy R1: Single signal with fraud probability < 0.70
        if fraud_probability < 0.70:
            return {
                "status": "INSUFFICIENT",
                "reason": "Policy R1 applies: investigation rests on a single weak signal with assessed probability < 0.70. Verify before blocking.",
                "missing_evidence": ["Direct customer transaction validation"],
                "recommended_evidence": [EvidenceRequestTypeEnum.CUSTOMER_VALIDATION],
            }

        return {
            "status": "SUFFICIENT",
            "reason": "Evidence sufficient to determine defensible next best actions under policy.",
            "missing_evidence": [],
            "recommended_evidence": [],
        }
