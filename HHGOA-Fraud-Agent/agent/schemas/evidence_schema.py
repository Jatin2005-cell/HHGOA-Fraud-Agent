"""Evidence and Evidence Request schemas conforming to IEEE-CIS Fraud Benchmark specification."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceSourceEnum(str, Enum):
    GRAPH = "graph"
    DOCUMENT = "document"
    CUSTOMER = "customer"
    EXTERNAL = "external"


class EvidenceItem(BaseModel):
    claim: str = Field(..., description="Factual evidence claim derived from graph, doc, or customer")
    source: EvidenceSourceEnum = Field(..., description="Source of the claim: graph | document | customer | external")
    ref: str = Field(..., description="Query name, document section, or request id")
    entity_ids: List[str] = Field(default_factory=list, description="IDs of entities the claim rests on")


class EvidenceRequestTypeEnum(str, Enum):
    CUSTOMER_VALIDATION = "customer_validation"
    STEP_UP_AUTH = "step_up_auth"
    ANALYST_INFO = "analyst_info"
    ADDITIONAL_TRANSACTION_CONTEXT = "additional_transaction_context"


class EvidenceRequest(BaseModel):
    type: EvidenceRequestTypeEnum = Field(..., description="Type of evidence requested")
    asked_after_step: int = Field(..., description="Investigation step number when requested")
    assumed_response: str = Field(..., description="Simulated/assumed response clearly identified as test evidence")
