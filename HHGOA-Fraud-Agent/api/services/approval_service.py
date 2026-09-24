"""Approval Service: Enforces human governance sign-off on L1/L2 action recommendations."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from case_management.case_repository import CaseRepository
from case_management.case_lifecycle import CaseLifecycleStatus
from case_management.audit_service import AuditService


class ApprovalService:
    def __init__(self, repository: Optional[CaseRepository] = None):
        self.repository = repository or CaseRepository()

    def get_approval_status(self, case_id: str) -> Dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        return {
            "case_id": case.case_id,
            "approval_route": case.approval_route,
            "approval_status": case.approval_status,
            "approval_details": case.approval_details,
        }

    def approve_action(
        self,
        case_id: str,
        approver_role: str,
        approver_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        # Critical Security Rule: LLM / Agent cannot approve its own action
        if approver_role.lower() in ["agent", "llm", "ai"]:
            raise ValueError("Autonomous agents cannot self-approve L1 or L2 action recommendations.")

        # Enforce role hierarchy: L2 actions require L2_FRAUD_MANAGER
        if case.approval_route == "L2" and approver_role != "L2_FRAUD_MANAGER":
            raise ValueError("L2 approval route strictly mandates authorization by L2_FRAUD_MANAGER.")

        approval_details = {
            "approver_role": approver_role,
            "approver_id": approver_id,
            "decision": "APPROVED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }

        updates = {
            "approval_status": "APPROVED",
            "approval_details": approval_details,
            "status": CaseLifecycleStatus.RESOLVED.value,
        }
        updated_case = self.repository.update_case(case_id, updates)

        AuditService.log_event(
            "ACTION_APPROVED",
            case_id,
            actor=f"{approver_role}:{approver_id}",
            status="SUCCESS",
            details=approval_details,
        )

        return {
            "case_id": case_id,
            "status": updated_case.status.value,
            "approval_status": "APPROVED",
            "approval_details": approval_details,
        }

    def reject_action(
        self,
        case_id: str,
        approver_role: str,
        approver_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        if approver_role.lower() in ["agent", "llm", "ai"]:
            raise ValueError("Autonomous agents cannot self-reject or self-govern actions.")

        rejection_details = {
            "approver_role": approver_role,
            "approver_id": approver_id,
            "decision": "REJECTED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }

        updates = {
            "approval_status": "REJECTED",
            "approval_details": rejection_details,
            "status": CaseLifecycleStatus.ESCALATED.value,
        }
        updated_case = self.repository.update_case(case_id, updates)

        AuditService.log_event(
            "ACTION_REJECTED",
            case_id,
            actor=f"{approver_role}:{approver_id}",
            status="SUCCESS",
            details=rejection_details,
        )

        return {
            "case_id": case_id,
            "status": updated_case.status.value,
            "approval_status": "REJECTED",
            "approval_details": rejection_details,
        }
