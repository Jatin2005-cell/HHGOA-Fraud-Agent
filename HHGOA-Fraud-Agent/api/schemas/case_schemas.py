"""Case API Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CaseResponse(BaseModel):
    case_id: str
    status: str
    created_at: str
    updated_at: str
    trigger_type: str
    trigger_text: str
    flagged_txn_id: str
    customer_id: str
    card_id: str
    verdict: str
    fraud_probability: Optional[float] = None
    risk_score: Optional[float] = None
    fraud_pattern: str
    pattern_description: str
    affected_txn_ids: List[str]
    exposure_usd: float
    connected_card_ids: List[str]
    connected_device_profiles: List[str]
    approval_route: str
    approval_status: str
    sar_required: bool
    sar_status: str
    summary: str
    stop_reason: str


class CaseListResponse(BaseModel):
    items: List[CaseResponse]
    total: int
    page: int
    page_size: int
