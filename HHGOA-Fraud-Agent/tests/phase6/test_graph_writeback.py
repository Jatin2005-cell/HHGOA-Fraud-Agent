"""Unit tests for Safe, Idempotent Graph Writeback."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from case_management.graph_writeback import CaseWritebackService, WritebackResult


def test_case_writeback_idempotency():
    service = CaseWritebackService()
    case_payload = {
        "case_id": "HHG-001",
        "flagged_txn_id": "3514030",
        "card_id": "C12382-K1",
        "status": "RESOLVED",
        "verdict": "legitimate",
        "fraud_probability": 0.12,
        "pattern": "none",
        "exposure_usd": 0.0,
        "summary": "Verified in-person transaction in normal billing region.",
        "stop_reason": "sufficient_evidence_for_action",
    }

    # First write: CREATED or UPDATED
    res1 = service.write_case(case_payload)
    assert res1.success is True
    assert res1.case_id == "HHG-001"
    assert "DynamicCase:HHG-001" in res1.vertices_written

    # Second write: must succeed without duplicating
    res2 = service.write_case(case_payload)
    assert res2.success is True
    assert res2.status in ["UPDATED", "UNCHANGED"]


def test_invalid_case_id_writeback():
    service = CaseWritebackService()
    bad_payload = {"case_id": "INVALID_ID_9999"}
    res = service.write_case(bad_payload)
    assert res.success is False
    assert "Invalid case_id format" in (res.error or "")


if __name__ == "__main__":
    test_case_writeback_idempotency()
    test_invalid_case_id_writeback()
    print("test_graph_writeback.py: ALL PASS")
