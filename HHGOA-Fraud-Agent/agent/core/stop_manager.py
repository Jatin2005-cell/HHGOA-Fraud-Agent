"""Stop-Condition Manager: Enforces deterministic investigation termination rules."""

from typing import Any, Dict, List
from agent.schemas.investigation_schema import VerdictEnum


class Tuple_Stop:
    should_stop: bool
    reason: str

    def __init__(self, should_stop: bool, reason: str):
        self.should_stop = should_stop
        self.reason = reason


class StopManager:
    """Evaluates whether investigation should terminate to prevent unbounded traversals."""

    MAX_STEPS = 10

    @classmethod
    def evaluate_stop(
        cls,
        step: int,
        fraud_probability: float,
        verdict: str,
        num_evidence_items: int,
        evidence_requests_made: int,
        tool_failure: bool = False,
    ) -> Tuple_Stop:
        """
        Returns:
            Tuple_Stop with should_stop boolean and reason string.
        """
        return should_investigation_stop(
            step=step,
            fraud_probability=fraud_probability,
            verdict=verdict,
            num_evidence_items=num_evidence_items,
            evidence_requests_made=evidence_requests_made,
            tool_failure=tool_failure,
        )


def should_investigation_stop(
    step: int,
    fraud_probability: float,
    verdict: str,
    num_evidence_items: int,
    evidence_requests_made: int,
    tool_failure: bool = False,
) -> Tuple_Stop:
    """Evaluates the 7 official stop conditions."""
    if tool_failure:
        return Tuple_Stop(True, "tool_failure: Investigation terminated due to MCP/graph tool communication failure.")

    if step >= StopManager.MAX_STEPS:
        return Tuple_Stop(True, f"maximum_steps_reached: Reached ceiling of {StopManager.MAX_STEPS} investigation steps.")

    # Verification response settled
    if evidence_requests_made > 0:
        return Tuple_Stop(
            True,
            "verification_response_settled: Direct customer verification received; policy actions definitively determined.",
        )

    # High certainty fraud
    if fraud_probability >= 0.85 and num_evidence_items >= 2:
        return Tuple_Stop(
            True,
            f"sufficient_evidence_for_action: Fraud probability {fraud_probability:.2f} supported by {num_evidence_items} graph signals.",
        )

    # High certainty legitimate
    if fraud_probability <= 0.15 and num_evidence_items >= 2:
        return Tuple_Stop(
            True,
            f"sufficient_evidence_for_action: Legitimate activity confirmed (fraud probability {fraud_probability:.2f}); alert cleared.",
        )

    # Default: continue if within budget
    return Tuple_Stop(False, "")
