"""Unit tests for Human Governance and Approval Workflow."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from case_management.case_repository import CaseRepository, DynamicCaseRecord
from case_management.case_lifecycle import CaseLifecycleStatus
from api.services.approval_service import ApprovalService


def test_agent_cannot_self_approve():
    repo = CaseRepository()
    case = DynamicCaseRecord(
        case_id="HHG-TEST-01",
        status=CaseLifecycleStatus.APPROVAL_PENDING,
        approval_route="L1",
        approval_status="PENDING",
    )
    repo.upsert_case(case)

    service = ApprovalService(repo)
    try:
        service.approve_action("HHG-TEST-01", approver_role="agent", approver_id="ai_agent", reason="Self approve")
        assert False, "Should have rejected agent self-approval"
    except ValueError as e:
        assert "cannot self-approve" in str(e)


def test_l1_team_lead_approval():
    repo = CaseRepository()
    case = DynamicCaseRecord(
        case_id="HHG-TEST-02",
        status=CaseLifecycleStatus.APPROVAL_PENDING,
        approval_route="L1",
        approval_status="PENDING",
    )
    repo.upsert_case(case)

    service = ApprovalService(repo)
    res = service.approve_action(
        case_id="HHG-TEST-02",
        approver_role="L1_TEAM_LEAD",
        approver_id="lead_sarah",
        reason="Verified testing sequence matches policy R5.",
    )
    assert res["approval_status"] == "APPROVED"
    assert res["status"] == CaseLifecycleStatus.RESOLVED.value


def test_l2_requires_fraud_manager():
    repo = CaseRepository()
    case = DynamicCaseRecord(
        case_id="HHG-TEST-03",
        status=CaseLifecycleStatus.APPROVAL_PENDING,
        approval_route="L2",
        approval_status="PENDING",
    )
    repo.upsert_case(case)

    service = ApprovalService(repo)
    # L1_TEAM_LEAD cannot approve L2 route
    try:
        service.approve_action("HHG-TEST-03", approver_role="L1_TEAM_LEAD", approver_id="lead_sarah", reason="Try L2")
        assert False, "Should have rejected L1 attempting L2 approval"
    except ValueError as e:
        assert "L2_FRAUD_MANAGER" in str(e)

    # Valid L2 Fraud Manager approval
    res = service.approve_action("HHG-TEST-03", approver_role="L2_FRAUD_MANAGER", approver_id="mgr_dave", reason="Confirmed $32k syndicate exposure.")
    assert res["approval_status"] == "APPROVED"


if __name__ == "__main__":
    test_agent_cannot_self_approve()
    test_l1_team_lead_approval()
    test_l2_requires_fraud_manager()
    print("test_approval_workflow.py: ALL PASS")
