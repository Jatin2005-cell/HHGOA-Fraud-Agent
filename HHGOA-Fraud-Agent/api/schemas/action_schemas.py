"""Action and Approval API Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ActionItemResponse(BaseModel):
    action: str
    route: str
    reason: str


class ActionResponse(BaseModel):
    case_id: str
    initial_actions: List[ActionItemResponse]
    final_actions: List[ActionItemResponse]
    what_changed: str
    approval_route: str
    approval_status: str


class ApprovalStatusResponse(BaseModel):
    case_id: str
    approval_route: str  # auto | L1 | L2
    approval_status: str  # NOT_REQUIRED | PENDING | APPROVED | REJECTED
    approval_details: Optional[Dict[str, Any]] = None
