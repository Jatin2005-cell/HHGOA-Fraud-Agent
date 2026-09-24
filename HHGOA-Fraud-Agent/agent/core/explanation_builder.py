"""Explanation Builder: Synthesizes multi-step evidence provenance into analyst explanations."""

from typing import Any, Dict, List
from agent.schemas.evidence_schema import EvidenceItem
from agent.schemas.investigation_schema import PatternEnum


class ExplanationBuilder:
    """Generates concise, human-auditable analyst summaries and rationales."""

    @classmethod
    def build_summary(
        cls,
        case_id: str,
        trigger_type: str,
        pattern: PatternEnum,
        pattern_description: str,
        fraud_prob: float,
        exposure_usd: float,
        evidence_items: List[EvidenceItem],
        assumed_response: str = "",
    ) -> str:
        """
        Builds a 2-6 sentence summary suitable for fraud analysts,
        synthesizing observed graph signals, precedents, and policy outcome.
        """
        top_claims = [e.claim for e in evidence_items[:3]]
        evidence_summary = " ".join(top_claims)

        pat_text = pattern.value.replace("_", " ").title()
        if pattern == PatternEnum.UNDOCUMENTED and pattern_description:
            pat_text = f"an undocumented pattern ({pattern_description})"

        summary = (
            f"Investigation of alert {case_id} ({trigger_type}) determined a fraud probability of {fraud_prob:.2f} "
            f"consistent with {pat_text}. {evidence_summary}"
        )

        if assumed_response:
            summary += f" Verification request completed ({assumed_response})."

        summary += f" Total identified exposure is ${exposure_usd:.2f}."
        return summary
