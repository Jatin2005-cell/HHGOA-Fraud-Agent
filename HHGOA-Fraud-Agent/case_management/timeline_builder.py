"""Investigation Timeline Builder: Constructs chronological event audit trail for cases."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str
    state: str
    actor: str  # agent | policy_engine | analyst | system
    description: str
    evidence_refs: List[str] = Field(default_factory=list)
    tool_name: Optional[str] = None
    status: str = "success"


class TimelineBuilder:
    """Constructs and manages chronological timelines for fraud investigations."""

    @classmethod
    def build_initial_timeline(
        cls, case_id: str, trigger_type: str, trigger_text: str
    ) -> List[TimelineEvent]:
        """Builds initial timeline events on case creation."""
        now = datetime.now(timezone.utc).isoformat()
        return [
            TimelineEvent(
                timestamp=now,
                event_type="CASE_CREATED",
                state="NEW",
                actor="system",
                description=f"Case {case_id} registered from trigger ({trigger_type}): {trigger_text}",
            )
        ]

    @classmethod
    def build_from_agent_output(
        cls, case_id: str, trigger_type: str, agent_output: Any
    ) -> List[TimelineEvent]:
        """Builds full chronological investigation timeline from Phase 5 agent output."""
        events: List[TimelineEvent] = []
        now = datetime.now(timezone.utc).isoformat()

        # 1. Creation
        events.append(
            TimelineEvent(
                timestamp=now,
                event_type="CASE_CREATED",
                state="NEW",
                actor="system",
                description=f"Case {case_id} created for investigation.",
            )
        )

        # 2. Investigation Started
        events.append(
            TimelineEvent(
                timestamp=now,
                event_type="INVESTIGATION_STARTED",
                state="INVESTIGATING",
                actor="agent",
                description="Agent launched autonomous graph investigation.",
            )
        )

        # 3. Evidence items & tool calls
        if hasattr(agent_output, "case") and agent_output.case:
            for ev in agent_output.case.evidence:
                events.append(
                    TimelineEvent(
                        timestamp=now,
                        event_type="EVIDENCE_RECEIVED",
                        state="INVESTIGATING",
                        actor="agent",
                        description=ev.claim,
                        evidence_refs=[ev.ref],
                        tool_name=ev.ref.split(":")[0] if ":" in ev.ref else None,
                    )
                )

        # 4. Pattern Identified & Risk Assessed
        if hasattr(agent_output, "case") and agent_output.case:
            verdict = agent_output.case.verdict.value if hasattr(agent_output.case.verdict, "value") else str(agent_output.case.verdict)
            pat = agent_output.case.pattern.value if hasattr(agent_output.case.pattern, "value") else str(agent_output.case.pattern)
            prob = agent_output.case.fraud_probability

            events.append(
                TimelineEvent(
                    timestamp=now,
                    event_type="RISK_ASSESSED",
                    state="REVIEW",
                    actor="agent",
                    description=f"Assessed fraud probability: {prob:.2f}, verdict: {verdict}.",
                )
            )
            events.append(
                TimelineEvent(
                    timestamp=now,
                    event_type="PATTERN_IDENTIFIED",
                    state="REVIEW",
                    actor="agent",
                    description=f"Identified pattern: {pat}.",
                )
            )

        # 5. Evidence Requests
        if hasattr(agent_output, "evidence_requests") and agent_output.evidence_requests:
            for req in agent_output.evidence_requests:
                events.append(
                    TimelineEvent(
                        timestamp=now,
                        event_type="EVIDENCE_REQUESTED",
                        state="EVIDENCE_PENDING",
                        actor="agent",
                        description=f"Requested {req.type.value if hasattr(req.type, 'value') else str(req.type)} at step {req.asked_after_step}.",
                    )
                )
                events.append(
                    TimelineEvent(
                        timestamp=now,
                        event_type="EVIDENCE_RECEIVED",
                        state="REVIEW",
                        actor="system",
                        description=req.assumed_response,
                    )
                )

        # 6. Policy Evaluated & Actions Recommended
        if hasattr(agent_output, "next_best_actions") and agent_output.next_best_actions:
            final_actions = agent_output.next_best_actions.final
            for act in final_actions:
                act_name = act.action.value if hasattr(act.action, "value") else str(act.action)
                route = act.route.value if hasattr(act.route, "value") else str(act.route)
                events.append(
                    TimelineEvent(
                        timestamp=now,
                        event_type="ACTION_RECOMMENDED",
                        state="ACTION_REQUIRED",
                        actor="policy_engine",
                        description=f"Action: {act_name}, Route: {route}, Reason: {act.reason}",
                    )
                )
                if route in ["L1", "L2"]:
                    events.append(
                        TimelineEvent(
                            timestamp=now,
                            event_type="APPROVAL_REQUESTED",
                            state="APPROVAL_PENDING",
                            actor="policy_engine",
                            description=f"Requires {route} approval for {act_name}.",
                        )
                    )

        # 7. SAR Generated
        if hasattr(agent_output, "sar") and agent_output.sar and agent_output.sar.file:
            events.append(
                TimelineEvent(
                    timestamp=now,
                    event_type="SAR_GENERATED",
                    state="RESOLVED",
                    actor="policy_engine",
                    description=f"SAR generated for regulator: {agent_output.sar.reason}",
                )
            )

        # 8. Resolved
        events.append(
            TimelineEvent(
                timestamp=now,
                event_type="CASE_RESOLVED",
                state="RESOLVED",
                actor="agent",
                description=f"Investigation concluded. Reason: {agent_output.stop_reason}",
            )
        )

        return events
