"""Agent Output Schema conforming to IEEE-CIS Fraud Benchmark specification."""

from typing import List, Optional
from pydantic import BaseModel, Field
from .evidence_schema import EvidenceRequest
from .action_schema import NextBestActions
from .investigation_schema import CaseRecord, SARRecord


class BenchmarkTrigger(BaseModel):
    case_id: str = Field(..., description="Benchmark case ID (e.g. HHG-001)")
    opened_at: str = Field(..., description="Timestamp when alert was opened")
    trigger_type: str = Field(..., description="Trigger source: risk_score | customer_report | analyst_request")
    trigger_text: str = Field(..., description="Raw alert or customer message text")
    flagged_txn_id: str = Field(..., description="ID of the flagged transaction")
    card_id: str = Field(..., description="Card identifier (e.g. C12382-K1)")
    customer_id: str = Field(..., description="Customer identifier (e.g. C12382)")
    risk_score: Optional[float] = Field(default=None, description="Model risk score if risk_score trigger")


class ProvenanceContract(BaseModel):
    execution_mode: str = Field(default="OFFLINE_STAGED_SIMULATION", description="LIVE_TIGERGRAPH | OFFLINE_STAGED_SIMULATION")
    graph_backend: str = Field(default="STAGED_DATASET", description="FraudInvestigationGraph | STAGED_DATASET")
    graph_verified: bool = Field(default=False, description="True if verified on live TigerGraph")
    mcp_verified: bool = Field(default=False, description="True if verified on live MCP server")
    writeback_verified: bool = Field(default=False, description="True if verified written to live TigerGraph")
    evidence_provenance: str = Field(default="LOCAL_STAGED_DATASET", description="TIGERGRAPH | LOCAL_STAGED_DATASET")


class AgentOutputSchema(BaseModel):
    case_id: str = Field(..., description="Unique case identifier from case_pack.csv")
    case: CaseRecord = Field(..., description="Part 1: Bank internal investigation record")
    evidence_requests: List[EvidenceRequest] = Field(default_factory=list, description="Requested additional evidence requests")
    next_best_actions: NextBestActions = Field(..., description="Part 3: Initial and final action recommendations")
    sar: SARRecord = Field(..., description="Part 2: Standalone regulatory filing")
    stop_reason: str = Field(..., description="Reason why the investigation concluded")
    tool_calls: int = Field(default=0, description="Total graph and retrieval tool calls made")
    tokens: Optional[int] = Field(default=None, description="Total LLM tokens consumed")
    latency_s: Optional[float] = Field(default=None, description="Total execution wall-clock seconds")
    provenance: ProvenanceContract = Field(default_factory=ProvenanceContract, description="Runtime provenance contract")
