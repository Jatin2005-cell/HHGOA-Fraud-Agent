"""Unit tests for intelligent Tool Selection logic."""

from agent.core.investigation_state import InvestigationState
from agent.core.tool_selector import ToolSelector


def test_initial_tool_selection():
    state = InvestigationState(
        case_id="HHG-001",
        trigger_type="risk_score",
        trigger_text="Test alert",
        flagged_txn_id="3514030",
        customer_id="C12382",
        card_id="C12382-K1",
    )
    # First tool must always be get_transaction_context
    next_tool = ToolSelector.select_next_tool(state)
    assert next_tool is not None
    tname, tparams, reason = next_tool
    assert tname == "get_transaction_context"
    assert tparams["transaction_id"] == 3514030


def test_channel_specific_tool_selection():
    state = InvestigationState(
        case_id="HHG-001",
        trigger_type="risk_score",
        trigger_text="Test alert",
        flagged_txn_id="3514030",
        customer_id="C12382",
        card_id="C12382-K1",
    )
    # Mock that get_transaction_context has already run for an in-person transaction
    state.tool_calls.append({"tool_name": "get_transaction_context"})
    state.graph_entities["target_transaction"] = {
        "txn_id": 3514030,
        "channel": "in_person",
        "card_id": "C12382-K1",
        "amount": 77.07,
    }

    next_tool = ToolSelector.select_next_tool(state)
    assert next_tool is not None
    tname, tparams, reason = next_tool
    # For in-person, it should select find_region_anomalies
    assert tname == "find_region_anomalies"
    assert tparams["card_id"] == "C12382-K1"


if __name__ == "__main__":
    test_initial_tool_selection()
    test_channel_specific_tool_selection()
    print("test_tool_selection.py: ALL PASS")
