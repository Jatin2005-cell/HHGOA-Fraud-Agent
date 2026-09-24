"""Automated Test Runner for Phase 5 Agent Test Suite."""

import os
import sys

# Ensure HHGOA-Fraud-Agent root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from agent.tests.test_state_machine import test_valid_state_transitions, test_invalid_state_transition
from agent.tests.test_tool_selection import test_initial_tool_selection, test_channel_specific_tool_selection
from agent.tests.test_policy_engine import test_approval_routing, test_policy_r1_verify_before_block, test_policy_r2_customer_denial
from agent.tests.test_graph_rag import test_document_store, test_evidence_ranker, test_case_memory_retrieval
from agent.tests.test_stop_conditions import test_stop_conditions
from agent.tests.test_agent_integration import test_agent_investigation_risk_score_case, test_agent_investigation_customer_report_case


def run_tests():
    print("=" * 60)
    print("RUNNING PHASE 5 AGENT & GRAPHRAG AUTOMATED TEST SUITE")
    print("=" * 60)

    tests = [
        ("test_valid_state_transitions", test_valid_state_transitions),
        ("test_invalid_state_transition", test_invalid_state_transition),
        ("test_initial_tool_selection", test_initial_tool_selection),
        ("test_channel_specific_tool_selection", test_channel_specific_tool_selection),
        ("test_approval_routing", test_approval_routing),
        ("test_policy_r1_verify_before_block", test_policy_r1_verify_before_block),
        ("test_policy_r2_customer_denial", test_policy_r2_customer_denial),
        ("test_document_store", test_document_store),
        ("test_evidence_ranker", test_evidence_ranker),
        ("test_case_memory_retrieval", test_case_memory_retrieval),
        ("test_stop_conditions", test_stop_conditions),
        ("test_agent_investigation_risk_score_case", test_agent_investigation_risk_score_case),
        ("test_agent_investigation_customer_report_case", test_agent_investigation_customer_report_case),
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print("=" * 60)
    print(f"TEST RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {len(tests)})")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
