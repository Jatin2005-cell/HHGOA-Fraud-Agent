"""Unit tests for Graph Readback Verification."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from case_management.graph_writeback import CaseWritebackService
from case_management.graph_readback import CaseReadbackService, ReadbackVerificationResult


def test_graph_readback_verified():
    # First ensure case is written
    writeback = CaseWritebackService()
    case_payload = {
        "case_id": "HHG-002",
        "flagged_txn_id": "3478782",
        "card_id": "C11891-K1",
        "status": "RESOLVED",
        "verdict": "legitimate",
        "fraud_probability": 0.14,
        "pattern": "none",
        "exposure_usd": 0.0,
        "summary": "Online purchase within customer baseline spend.",
        "stop_reason": "sufficient_evidence_for_action",
    }
    writeback.write_case(case_payload)

    # Readback
    readback = CaseReadbackService()
    res = readback.verify_case("HHG-002")

    assert res.writeback_status == "VERIFIED"
    assert res.case_id == "HHG-002"
    assert "DynamicCase:HHG-002" in res.verified_entities
    assert any("CASE_INVOLVES" in rel for rel in res.verified_relationships)


def test_graph_readback_not_found():
    readback = CaseReadbackService()
    res = readback.verify_case("HHG-999")
    assert res.writeback_status == "VERIFICATION_FAILED"


if __name__ == "__main__":
    test_graph_readback_verified()
    test_graph_readback_not_found()
    print("test_graph_readback.py: ALL PASS")
