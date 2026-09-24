"""Unit tests for Stop Conditions evaluation."""

from agent.core.stop_manager import should_investigation_stop, StopManager


def test_stop_conditions():
    # 1. High probability fraud with multiple evidence items
    res1 = should_investigation_stop(
        step=3,
        fraud_probability=0.88,
        verdict="fraud",
        num_evidence_items=4,
        evidence_requests_made=0,
    )
    assert res1.should_stop
    assert "sufficient_evidence_for_action" in res1.reason

    # 2. Maximum steps ceiling reached
    res2 = should_investigation_stop(
        step=StopManager.MAX_STEPS,
        fraud_probability=0.50,
        verdict="uncertain",
        num_evidence_items=1,
        evidence_requests_made=0,
    )
    assert res2.should_stop
    assert "maximum_steps_reached" in res2.reason

    # 3. Verification response settled
    res3 = should_investigation_stop(
        step=2,
        fraud_probability=0.86,
        verdict="fraud",
        num_evidence_items=3,
        evidence_requests_made=1,
    )
    assert res3.should_stop
    assert "verification_response_settled" in res3.reason


if __name__ == "__main__":
    test_stop_conditions()
    print("test_stop_conditions.py: ALL PASS")
