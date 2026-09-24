"""Investigation Case and SAR schemas conforming to IEEE-CIS Fraud Benchmark specification."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from .evidence_schema import EvidenceItem


class CaseStatusEnum(str, Enum):
    OPEN = "open"
    CLOSED_FRAUD = "closed_fraud"
    CLOSED_LEGITIMATE = "closed_legitimate"
    ESCALATED = "escalated"


class VerdictEnum(str, Enum):
    FRAUD = "fraud"
    LEGITIMATE = "legitimate"
    UNCERTAIN = "uncertain"


class PatternEnum(str, Enum):
    CARD_TESTING = "card_testing"
    CARD_NOT_PRESENT_FRAUD = "card_not_present_fraud"
    CARD_NOT_PRESENT_NEW_DEVICE = "card_not_present_new_device"
    OUT_OF_REGION_USE = "out_of_region_use"
    ACCOUNT_TAKEOVER = "account_takeover"
    UNDOCUMENTED = "undocumented"
    NONE = "none"


class CaseRecord(BaseModel):
    status: CaseStatusEnum = Field(..., description="Investigation status: open | closed_fraud | closed_legitimate | escalated")
    verdict: VerdictEnum = Field(..., description="Conclusion: fraud | legitimate | uncertain")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Assessed probability between 0 and 1")
    pattern: PatternEnum = Field(..., description="Identified fraud pattern enum or 'none'")
    pattern_description: str = Field(default="", description="Description required if pattern is undocumented, otherwise empty")
    affected_txn_ids: List[str] = Field(default_factory=list, description="Every transaction in the fraud episode")
    first_suspicious_txn_id: str = Field(default="", description="Where the suspicious activity started")
    connected_card_ids: List[str] = Field(default_factory=list, description="Other cards caught in the same compromise or device")
    connected_device_profiles: List[str] = Field(default_factory=list, description="Device profiles linking this case to other cards")
    exposure_usd: float = Field(default=0.0, ge=0.0, description="Sum of absolute amounts of affected transactions in USD")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Structured factual claims with provenance")
    similar_prior_cases: List[str] = Field(default_factory=list, description="Retrieved closed cases used as memory (e.g. CC-0141)")
    summary: str = Field(..., description="Concise investigation synthesis for fraud analysts")
    written_to_graph: bool = Field(default=False, description="Whether case record was registered in TigerGraph memory")
    graph_case_id: str = Field(default="", description="ID of the graph DynamicCase vertex created, if any")


class SARRecord(BaseModel):
    file: bool = Field(..., description="Whether a suspicious activity report should be filed")
    reason: str = Field(..., description="Why file, or why not. Citing the policy rule")
    narrative: str = Field(default="", description="Complete standalone regulatory narrative (who, what, when, where, how, why)")
    subjects: List[str] = Field(default_factory=list, description="IDs of customers, cards, devices, merchants named")
    total_amount_usd: float = Field(default=0.0, ge=0.0, description="Total suspicious activity amount in USD")
    activity_dates: List[str] = Field(default_factory=list, description="Start and end dates [YYYY-MM-DD, YYYY-MM-DD]")
