"""Unit tests for Dynamic Case Memory Writer."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from case_management.case_memory_writer import CaseMemoryWriter


def test_case_memory_registration():
    writer = CaseMemoryWriter()
    case_payload = {
        "case_id": "HHG-003",
        "customer_id": "C08623",
        "card_id": "C08623-K2",
        "flagged_txn_id": "3530164",
        "verdict": "fraud",
        "fraud_pattern": "card_not_present_fraud",
        "exposure_usd": 49.0,
        "affected_txn_ids": ["3530164"],
        "summary": "Customer confirmed dispute on unauthorized online transaction.",
        "sar_required": False,
        "final_next_best_action": [{"action": "BLOCK_CARD"}, {"action": "CREATE_CASE"}],
    }

    success = writer.register_case_in_memory(case_payload)
    assert success is True
    assert os.path.exists(writer.dynamic_memory_csv)

    # Re-registering updates the record idempotently
    success2 = writer.register_case_in_memory(case_payload)
    assert success2 is True


if __name__ == "__main__":
    test_case_memory_registration()
    print("test_case_memory.py: ALL PASS")
