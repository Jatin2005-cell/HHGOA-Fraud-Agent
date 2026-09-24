"""API Request Schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class InvestigationCreateRequest(BaseModel):
    case_id: str = Field(..., description="Unique case identifier (e.g. HHG-003)")
    trigger_type: str = Field(..., description="risk_score | customer_report | analyst_request")
    trigger_text: str = Field(..., description="Alert description or customer dispute message")
    flagged_txn_id: str = Field(..., description="Target 7-digit transaction ID")
    customer_id: str = Field(..., description="Customer ID (e.g. C08623)")
    card_id: str = Field(..., description="Card ID (e.g. C08623-K2)")
    risk_score: Optional[float] = Field(default=None, description="Optional model risk score")


class EvidenceRequestPayload(BaseModel):
    request_type: str = Field(..., description="customer_validation | step_up_auth | analyst_info")
    question: str = Field(..., description="Clarifying question or verification challenge")
    assumed_response: str = Field(..., description="Simulated response for test environment")


class ApprovalDecisionPayload(BaseModel):
    approver_role: str = Field(..., description="L1_TEAM_LEAD | L2_FRAUD_MANAGER")
    approver_id: str = Field(..., description="Analyst identifier")
    reason: str = Field(..., description="Governance justification for decision")
