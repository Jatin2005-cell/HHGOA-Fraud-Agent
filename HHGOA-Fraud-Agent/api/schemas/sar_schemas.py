"""SAR API Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SARResponse(BaseModel):
    case_id: str
    file: bool
    reason: str
    narrative: str
    subjects: List[str]
    total_amount_usd: float
    activity_dates: List[str]
    status: str  # NOT_REQUIRED | PENDING | GENERATED | REVIEW_REQUIRED
