"""Unit tests for FastAPI REST Endpoints."""

import os
import sys
from starlette.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from api.main import app

client = TestClient(app)


def test_health_endpoints():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"

    res_dep = client.get("/health/dependencies")
    assert res_dep.status_code == 200
    dep_data = res_dep.json()
    assert "tigergraph_engine" in dep_data["data"]["dependencies"]


def test_investigation_creation_endpoint():
    import time
    cid = f"HHG-API-{int(time.time() * 1000) % 900 + 100}"
    payload = {
        "case_id": cid,
        "trigger_type": "risk_score",
        "trigger_text": "Model scored transaction at 0.75",
        "flagged_txn_id": "3514030",
        "customer_id": "C12382",
        "card_id": "C12382-K1",
        "risk_score": 0.75,
    }
    res = client.post("/api/investigations", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["data"]["case_id"] == cid


def test_destructive_gsql_rejection():
    bad_payload = {
        "case_id": "HHG-API-BAD",
        "trigger_type": "risk_score",
        "trigger_text": "DROP GRAPH FraudInvestigationGraph",
        "flagged_txn_id": "3514030",
        "customer_id": "C12382",
        "card_id": "C12382-K1",
    }
    res = client.post("/api/investigations", json=bad_payload)
    assert res.status_code == 400
    body = res.json()
    assert body["success"] is False
    assert "Destructive database keywords detected" in body["error"]["message"]


def test_cases_listing_and_pagination():
    res = client.get("/api/cases?page=1&page_size=10")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "items" in body["data"]
    assert "total" in body["data"]


if __name__ == "__main__":
    test_health_endpoints()
    test_investigation_creation_endpoint()
    test_destructive_gsql_rejection()
    test_cases_listing_and_pagination()
    print("test_api.py: ALL PASS")
