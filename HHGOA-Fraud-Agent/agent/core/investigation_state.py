"""Investigation State Machine for Fraud Investigation Agent."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InvestigationStateEnum(str, Enum):
    TRIGGERED = "TRIGGERED"
    INITIALIZED = "INITIALIZED"
    EVIDENCE_COLLECTION = "EVIDENCE_COLLECTION"
    GRAPH_ANALYSIS = "GRAPH_ANALYSIS"
    CASE_MEMORY_RETRIEVAL = "CASE_MEMORY_RETRIEVAL"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    PATTERN_ASSESSMENT = "PATTERN_ASSESSMENT"
    UNCERTAINTY_ASSESSMENT = "UNCERTAINTY_ASSESSMENT"
    EVIDENCE_DECISION = "EVIDENCE_DECISION"
    REQUEST_MORE_EVIDENCE = "REQUEST_MORE_EVIDENCE"
    SUFFICIENT_EVIDENCE = "SUFFICIENT_EVIDENCE"
    NEXT_BEST_ACTION = "NEXT_BEST_ACTION"
    POLICY_VALIDATION = "POLICY_VALIDATION"
    APPROVAL_ROUTING = "APPROVAL_ROUTING"
    CASE_SUMMARY = "CASE_SUMMARY"
    MEMORY_UPDATE = "MEMORY_UPDATE"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"


class StateTransitionLog(BaseModel):
    from_state: InvestigationStateEnum
    to_state: InvestigationStateEnum
    timestamp: str
    step: int
    reason: str = ""


# Valid State Transitions
VALID_TRANSITIONS = {
    InvestigationStateEnum.TRIGGERED: {
        InvestigationStateEnum.INITIALIZED,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.INITIALIZED: {
        InvestigationStateEnum.EVIDENCE_COLLECTION,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.EVIDENCE_COLLECTION: {
        InvestigationStateEnum.GRAPH_ANALYSIS,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.GRAPH_ANALYSIS: {
        InvestigationStateEnum.CASE_MEMORY_RETRIEVAL,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.CASE_MEMORY_RETRIEVAL: {
        InvestigationStateEnum.RISK_ASSESSMENT,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.RISK_ASSESSMENT: {
        InvestigationStateEnum.PATTERN_ASSESSMENT,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.PATTERN_ASSESSMENT: {
        InvestigationStateEnum.UNCERTAINTY_ASSESSMENT,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.UNCERTAINTY_ASSESSMENT: {
        InvestigationStateEnum.EVIDENCE_DECISION,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.EVIDENCE_DECISION: {
        InvestigationStateEnum.REQUEST_MORE_EVIDENCE,
        InvestigationStateEnum.SUFFICIENT_EVIDENCE,
        InvestigationStateEnum.ESCALATED,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.REQUEST_MORE_EVIDENCE: {
        InvestigationStateEnum.EVIDENCE_COLLECTION,
        InvestigationStateEnum.SUFFICIENT_EVIDENCE,
        InvestigationStateEnum.NEXT_BEST_ACTION,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.SUFFICIENT_EVIDENCE: {
        InvestigationStateEnum.NEXT_BEST_ACTION,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.NEXT_BEST_ACTION: {
        InvestigationStateEnum.POLICY_VALIDATION,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.POLICY_VALIDATION: {
        InvestigationStateEnum.APPROVAL_ROUTING,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.APPROVAL_ROUTING: {
        InvestigationStateEnum.CASE_SUMMARY,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.CASE_SUMMARY: {
        InvestigationStateEnum.MEMORY_UPDATE,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.MEMORY_UPDATE: {
        InvestigationStateEnum.COMPLETED,
        InvestigationStateEnum.ESCALATED,
        InvestigationStateEnum.FAILED,
    },
    InvestigationStateEnum.COMPLETED: set(),
    InvestigationStateEnum.ESCALATED: {InvestigationStateEnum.COMPLETED},
    InvestigationStateEnum.FAILED: set(),
}


class InvestigationState(BaseModel):
    case_id: str
    trigger_type: str
    trigger_text: str
    flagged_txn_id: str
    customer_id: str
    card_id: str
    risk_score: Optional[float] = None
    opened_at: Optional[str] = None

    current_state: InvestigationStateEnum = InvestigationStateEnum.TRIGGERED
    investigation_step: int = 0
    transition_history: List[StateTransitionLog] = Field(default_factory=list)

    # Evidence and Graph
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_sources: List[str] = Field(default_factory=list)
    graph_entities: Dict[str, Any] = Field(default_factory=dict)
    graph_relationships: List[Dict[str, Any]] = Field(default_factory=list)
    similar_cases: List[str] = Field(default_factory=list)

    # Assessments
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    fraud_pattern: str = "none"
    pattern_description: str = ""
    uncertainty: Dict[str, Any] = Field(default_factory=dict)
    exposure: float = 0.0
    affected_txn_ids: List[str] = Field(default_factory=list)
    first_suspicious_txn_id: str = ""
    connected_card_ids: List[str] = Field(default_factory=list)
    connected_device_profiles: List[str] = Field(default_factory=list)

    # Decisions & Actions
    evidence_requests: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_actions: List[Dict[str, Any]] = Field(default_factory=list)
    validated_action: List[Dict[str, Any]] = Field(default_factory=list)
    initial_actions: List[Dict[str, Any]] = Field(default_factory=list)
    final_actions: List[Dict[str, Any]] = Field(default_factory=list)
    what_changed: str = "nothing"
    approval_route: str = "auto"
    explanation: Dict[str, Any] = Field(default_factory=dict)
    verdict: str = "uncertain"
    status: str = "open"
    sar: Dict[str, Any] = Field(default_factory=dict)

    # Execution telemetry
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    timestamps: Dict[str, str] = Field(default_factory=dict)
    stop_reason: str = ""
    tokens: Optional[int] = 0
    latency_s: Optional[float] = 0.0

    def transition_to(self, new_state: InvestigationStateEnum, reason: str = "") -> None:
        """Transitions the state machine to a new state if allowable, logging the transition."""
        allowed_next = VALID_TRANSITIONS.get(self.current_state, set())
        if new_state not in allowed_next:
            raise ValueError(
                f"Invalid state transition from {self.current_state.value} to {new_state.value}. "
                f"Allowed transitions: {[s.value for s in allowed_next]}"
            )

        log = StateTransitionLog(
            from_state=self.current_state,
            to_state=new_state,
            timestamp=datetime.now(timezone.utc).isoformat(),
            step=self.investigation_step,
            reason=reason,
        )
        self.transition_history.append(log)
        self.current_state = new_state
        self.investigation_step += 1
        self.timestamps[new_state.value] = datetime.now(timezone.utc).isoformat()
