"""Approval Workflow API Routes."""

from fastapi import APIRouter, Depends
from typing import Any, Dict

from api.schemas.request_schemas import ApprovalDecisionPayload
from api.schemas.response_schemas import ApiResponse
from api.routes.investigations import approval_service
from api.middleware.security import verify_api_security, sanitize_input_string

router = APIRouter(prefix="/api/approvals", tags=["Approvals"], dependencies=[Depends(verify_api_security)])


@router.post("/{case_id}/approve", response_model=ApiResponse[Dict[str, Any]])
def approve_case_action(case_id: str, payload: ApprovalDecisionPayload):
    """Simulates approval authorization by an L1 Team Lead or L2 Fraud Manager."""
    role = sanitize_input_string(payload.approver_role)
    approver = sanitize_input_string(payload.approver_id)
    reason = sanitize_input_string(payload.reason)

    result = approval_service.approve_action(
        case_id=case_id,
        approver_role=role,
        approver_id=approver,
        reason=reason,
    )
    return ApiResponse(success=True, data=result, error=None)


@router.post("/{case_id}/reject", response_model=ApiResponse[Dict[str, Any]])
def reject_case_action(case_id: str, payload: ApprovalDecisionPayload):
    """Simulates rejection of action recommendation by a human supervisor."""
    role = sanitize_input_string(payload.approver_role)
    approver = sanitize_input_string(payload.approver_id)
    reason = sanitize_input_string(payload.reason)

    result = approval_service.reject_action(
        case_id=case_id,
        approver_role=role,
        approver_id=approver,
        reason=reason,
    )
    return ApiResponse(success=True, data=result, error=None)
