"""Evidence API Schemas."""

from typing import List
from pydantic import BaseModel, Field


class EvidenceClaimResponse(BaseModel):
    claim: str
    source: str
    ref: str
    entity_ids: List[str]


class EvidenceResponse(BaseModel):
    case_id: str
    total_claims: int
    evidence: List[EvidenceClaimResponse]
    similar_prior_cases: List[str]
