"""Action and Approval schemas conforming to Fraud Policy v1.0."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ActionEnum(str, Enum):
    ALLOW_TRANSACTION = "ALLOW_TRANSACTION"
    DECLINE_TRANSACTION = "DECLINE_TRANSACTION"
    MONITOR_CARD = "MONITOR_CARD"
    MONITOR_CONNECTED_CARDS = "MONITOR_CONNECTED_CARDS"
    WARN_CUSTOMER = "WARN_CUSTOMER"
    VERIFY_WITH_CUSTOMER = "VERIFY_WITH_CUSTOMER"
    STEP_UP_AUTH = "STEP_UP_AUTH"
    BLOCK_CARD = "BLOCK_CARD"
    BLOCK_ALL_CARDS = "BLOCK_ALL_CARDS"
    GENERATE_REPORT = "GENERATE_REPORT"
    CREATE_CASE = "CREATE_CASE"
    FILE_REPORT = "FILE_REPORT"
    ESCALATE_TO_ANALYST = "ESCALATE_TO_ANALYST"
    CLOSE_NO_FRAUD = "CLOSE_NO_FRAUD"


class ApprovalRouteEnum(str, Enum):
    AUTO = "auto"
    L1 = "L1"
    L2 = "L2"


class ActionItem(BaseModel):
    action: ActionEnum = Field(..., description="Action from the Fraud Policy")
    route: ApprovalRouteEnum = Field(..., description="Approval route: auto | L1 | L2")
    reason: str = Field(..., description="Policy justification citing the rule number (e.g. R1, R2)")


class NextBestActions(BaseModel):
    initial: List[ActionItem] = Field(..., description="Actions recommended before any requested evidence came back")
    final: List[ActionItem] = Field(..., description="Actions recommended after assumed responses in evidence_requests")
    what_changed: str = Field(default="nothing", description="Explanation of why final differs from initial, or 'nothing'")
