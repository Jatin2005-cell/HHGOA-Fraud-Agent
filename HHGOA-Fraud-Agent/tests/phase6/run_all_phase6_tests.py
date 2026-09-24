"""Master Test Suite Runner for Phase 6."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.phase6.test_case_lifecycle import test_valid_lifecycle_transitions, test_illegal_lifecycle_transitions
from tests.phase6.test_graph_writeback import test_case_writeback_idempotency, test_invalid_case_id_writeback
from tests.phase6.test_graph_readback import test_graph_readback_verified, test_graph_readback_not_found
from tests.phase6.test_case_memory import test_case_memory_registration
from tests.phase6.test_sar import test_sar_generation_mandated, test_sar_generation_not_required, test_sar_validator_incomplete_narrative
from tests.phase6.test_approval_workflow import test_agent_cannot_self_approve, test_l1_team_lead_approval, test_l2_requires_fraud_manager
from tests.phase6.test_api import test_health_endpoints, test_investigation_creation_endpoint, test_destructive_gsql_rejection, test_cases_listing_and_pagination
from tests.phase6.test_end_to_end import test_complete_end_to_end_investigation


def run_tests():
    print("=" * 65)
    print("RUNNING PHASE 6 GRAPH WRITEBACK & API AUTOMATED TEST SUITE")
    print("=" * 65)

    test_cases = [
        ("test_valid_lifecycle_transitions", test_valid_lifecycle_transitions),
        ("test_illegal_lifecycle_transitions", test_illegal_lifecycle_transitions),
        ("test_case_writeback_idempotency", test_case_writeback_idempotency),
        ("test_invalid_case_id_writeback", test_invalid_case_id_writeback),
        ("test_graph_readback_verified", test_graph_readback_verified),
        ("test_graph_readback_not_found", test_graph_readback_not_found),
        ("test_case_memory_registration", test_case_memory_registration),
        ("test_sar_generation_mandated", test_sar_generation_mandated),
        ("test_sar_generation_not_required", test_sar_generation_not_required),
        ("test_sar_validator_incomplete_narrative", test_sar_validator_incomplete_narrative),
        ("test_agent_cannot_self_approve", test_agent_cannot_self_approve),
        ("test_l1_team_lead_approval", test_l1_team_lead_approval),
        ("test_l2_requires_fraud_manager", test_l2_requires_fraud_manager),
        ("test_health_endpoints", test_health_endpoints),
        ("test_investigation_creation_endpoint", test_investigation_creation_endpoint),
        ("test_destructive_gsql_rejection", test_destructive_gsql_rejection),
        ("test_cases_listing_and_pagination", test_cases_listing_and_pagination),
        ("test_complete_end_to_end_investigation", test_complete_end_to_end_investigation),
    ]

    passed = 0
    failed = 0

    for name, fn in test_cases:
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print("=" * 65)
    print(f"PHASE 6 TEST RESULTS: {passed} PASSED, {failed} FAILED (TOTAL {len(test_cases)})")
    print("=" * 65)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
