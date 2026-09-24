"""Integration tests for end-to-end agent investigation on real benchmark cases."""

from agent.schemas.agent_output_schema import BenchmarkTrigger, AgentOutputSchema
from agent.core.investigation_orchestrator import InvestigationOrchestrator


def test_agent_investigation_risk_score_case():
    trigger = BenchmarkTrigger(
        case_id="HHG-001",
        opened_at="2016-12-05 01:55:28",
        trigger_type="risk_score",
        trigger_text="Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide.",
        flagged_txn_id="3514030",
        card_id="C12382-K1",
        customer_id="C12382",
        risk_score=0.61,
    )

    orchestrator = InvestigationOrchestrator()
    output = orchestrator.investigate(trigger)

    assert isinstance(output, AgentOutputSchema)
    assert output.case_id == "HHG-001"
    assert output.tool_calls > 0
    assert len(output.case.evidence) > 0
    assert output.stop_reason != ""
    assert output.next_best_actions.initial is not None
    assert output.next_best_actions.final is not None


def test_agent_investigation_customer_report_case():
    trigger = BenchmarkTrigger(
        case_id="HHG-003",
        opened_at="2016-12-10 15:01:21",
        trigger_type="customer_report",
        trigger_text="Customer C08623 message: 'I never made this $49.00 purchase. Please check my card.' Refers to 3530164.",
        flagged_txn_id="3530164",
        card_id="C08623-K2",
        customer_id="C08623",
        risk_score=None,
    )

    orchestrator = InvestigationOrchestrator()
    output = orchestrator.investigate(trigger)

    assert output.case_id == "HHG-003"
    assert output.case.verdict.value in ["fraud", "uncertain", "legitimate"]
    assert len(output.evidence_requests) > 0  # customer dispute trigger asks for verification
    assert output.case.written_to_graph is True


if __name__ == "__main__":
    test_agent_investigation_risk_score_case()
    test_agent_investigation_customer_report_case()
    print("test_agent_integration.py: ALL PASS")
