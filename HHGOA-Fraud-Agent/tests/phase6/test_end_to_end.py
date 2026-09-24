"""End-to-End Investigation and API Integration Test on Real Case HHG-003."""

import os
import sys
from starlette.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from api.main import app
from case_management.graph_readback import CaseReadbackService

client = TestClient(app)


def test_complete_end_to_end_investigation():
    # 1. Register Investigation
    payload = {
        "case_id": "HHG-003",
        "trigger_type": "customer_report",
        "trigger_text": "Customer C08623 message: 'I never made this $49.00 purchase. Please check my card.' Refers to 3530164.",
        "flagged_txn_id": "3530164",
        "card_id": "C08623-K2",
        "customer_id": "C08623",
        "risk_score": None,
    }
    res1 = client.post("/api/investigations", json=payload)
    # Either 201 Created or 400 if already created
    assert res1.status_code in [201, 400]

    # 2. Run Phase 5 Investigation Agent
    res2 = client.post("/api/investigations/HHG-003/run")
    if res2.status_code != 200:
        print("res2 error:", res2.status_code, res2.text)
    assert res2.status_code == 200
    run_data = res2.json()["data"]
    assert run_data["case_id"] == "HHG-003"
    assert run_data["writeback_status"] == "VERIFIED"
    assert run_data["verdict"] in ["fraud", "uncertain", "legitimate"]

    # 3. GET Case Record
    res3 = client.get("/api/investigations/HHG-003")
    assert res3.status_code == 200
    case_rec = res3.json()["data"]
    assert case_rec["case_id"] == "HHG-003"
    assert case_rec["card_id"] == "C08623-K2"

    # 4. GET Timeline
    res4 = client.get("/api/investigations/HHG-003/timeline")
    assert res4.status_code == 200
    timeline = res4.json()["data"]
    assert len(timeline) > 0
    assert any(t["event_type"] == "CASE_CREATED" for t in timeline)

    # 5. GET Evidence
    res5 = client.get("/api/investigations/HHG-003/evidence")
    assert res5.status_code == 200
    ev = res5.json()["data"]
    assert ev["total_claims"] > 0

    # 6. GET Actions
    res6 = client.get("/api/investigations/HHG-003/actions")
    assert res6.status_code == 200
    acts = res6.json()["data"]
    assert len(acts["final_actions"]) > 0

    # 7. GET Approval
    res7 = client.get("/api/investigations/HHG-003/approval")
    assert res7.status_code == 200
    appr = res7.json()["data"]
    assert appr["approval_status"] in ["PENDING", "APPROVED", "NOT_REQUIRED"]

    # 8. GET SAR
    res8 = client.get("/api/investigations/HHG-003/sar")
    assert res8.status_code == 200
    sar = res8.json()["data"]
    assert "file" in sar

    # 9. Verify Graph Readback
    readback = CaseReadbackService()
    rb = readback.verify_case("HHG-003")
    assert rb.writeback_status == "VERIFIED"
    assert "DynamicCase:HHG-003" in rb.verified_entities

    # 10. Verify Duplicate Case Prevention
    res_dup = client.post("/api/investigations", json=payload)
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["error"]["message"]


if __name__ == "__main__":
    import traceback
    try:
        test_complete_end_to_end_investigation()
        print("test_end_to_end.py: ALL PASS")
    except Exception as e:
        traceback.print_exc()
        raise
