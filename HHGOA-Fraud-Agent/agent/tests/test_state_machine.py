"""Unit tests for Investigation State Machine and transition enforcement."""

from agent.core.investigation_state import (
    InvestigationState,
    InvestigationStateEnum,
    VALID_TRANSITIONS,
)


def test_valid_state_transitions():
    state = InvestigationState(
        case_id="HHG-001",
        trigger_type="risk_score",
        trigger_text="Test alert",
        flagged_txn_id="3514030",
        customer_id="C12382",
        card_id="C12382-K1",
    )
    assert state.current_state == InvestigationStateEnum.TRIGGERED

    # Valid step progression
    state.transition_to(InvestigationStateEnum.INITIALIZED, "Initializing case")
    assert state.current_state == InvestigationStateEnum.INITIALIZED
    assert state.investigation_step == 1

    state.transition_to(InvestigationStateEnum.EVIDENCE_COLLECTION, "Starting tools")
    assert state.current_state == InvestigationStateEnum.EVIDENCE_COLLECTION

    state.transition_to(InvestigationStateEnum.GRAPH_ANALYSIS, "Graph analyzed")
    assert state.current_state == InvestigationStateEnum.GRAPH_ANALYSIS


def test_invalid_state_transition():
    state = InvestigationState(
        case_id="HHG-001",
        trigger_type="risk_score",
        trigger_text="Test alert",
        flagged_txn_id="3514030",
        customer_id="C12382",
        card_id="C12382-K1",
    )
    # Skipping directly from TRIGGERED to COMPLETED must fail
    try:
        state.transition_to(InvestigationStateEnum.COMPLETED, "Illegal leap")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid state transition" in str(e)


if __name__ == "__main__":
    test_valid_state_transitions()
    test_invalid_state_transition()
    print("test_state_machine.py: ALL PASS")
