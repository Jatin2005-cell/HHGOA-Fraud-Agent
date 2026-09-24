"""Investigation Service: Orchestrates autonomous agent runs, graph writeback, and persistence."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from case_management.case_lifecycle import CaseLifecycleStatus
from case_management.case_repository import CaseRepository, DynamicCaseRecord
from case_management.graph_writeback import CaseWritebackService
from case_management.graph_readback import CaseReadbackService
from case_management.case_memory_writer import CaseMemoryWriter
from case_management.timeline_builder import TimelineBuilder, TimelineEvent
from case_management.audit_service import AuditService

from agent.core.investigation_orchestrator import InvestigationOrchestrator
from agent.schemas.agent_output_schema import BenchmarkTrigger
from sar.sar_generator import SARGenerator


class InvestigationService:
    def __init__(
        self,
        repository: Optional[CaseRepository] = None,
        orchestrator: Optional[InvestigationOrchestrator] = None,
        writeback: Optional[CaseWritebackService] = None,
        readback: Optional[CaseReadbackService] = None,
        memory_writer: Optional[CaseMemoryWriter] = None,
    ):
        self.repository = repository or CaseRepository()
        self.orchestrator = orchestrator or InvestigationOrchestrator()
        self.writeback = writeback or CaseWritebackService()
        self.readback = readback or CaseReadbackService()
        self.memory_writer = memory_writer or CaseMemoryWriter()
        self._timelines: Dict[str, List[TimelineEvent]] = {}

    def create_investigation(self, payload: Dict[str, Any]) -> DynamicCaseRecord:
        case_id = payload["case_id"]
        record = DynamicCaseRecord(
            case_id=case_id,
            status=CaseLifecycleStatus.NEW,
            trigger_type=payload["trigger_type"],
            trigger_text=payload["trigger_text"],
            flagged_txn_id=str(payload["flagged_txn_id"]),
            customer_id=payload["customer_id"],
            card_id=payload["card_id"],
            risk_score=payload.get("risk_score"),
        )
        created = self.repository.create_case(record)
        self._timelines[case_id] = TimelineBuilder.build_initial_timeline(
            case_id=case_id,
            trigger_type=record.trigger_type,
            trigger_text=record.trigger_text,
        )
        AuditService.log_event("INVESTIGATION_CREATED", case_id, "investigation_service", "SUCCESS")
        return created

    def run_investigation(self, case_id: str) -> Dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        # Update lifecycle to INVESTIGATING
        self.repository.update_case(case_id, {"status": CaseLifecycleStatus.INVESTIGATING.value})
        AuditService.log_event("INVESTIGATION_STARTED", case_id, "investigation_agent", "SUCCESS")

        # 1. Invoke Phase 5 Agent Orchestrator
        trigger = BenchmarkTrigger(
            case_id=case.case_id,
            opened_at=case.created_at,
            trigger_type=case.trigger_type,
            trigger_text=case.trigger_text,
            flagged_txn_id=case.flagged_txn_id,
            card_id=case.card_id,
            customer_id=case.customer_id,
            risk_score=case.risk_score,
        )

        agent_output = self.orchestrator.investigate(trigger)

        # 2. Build Timeline Events
        timeline_events = TimelineBuilder.build_from_agent_output(case_id, case.trigger_type, agent_output)
        self._timelines[case_id] = timeline_events

        # 3. Determine Approval Status
        highest_route = "auto"
        for act in agent_output.next_best_actions.final:
            r = act.route.value if hasattr(act.route, "value") else str(act.route)
            if r == "L2":
                highest_route = "L2"
                break
            elif r == "L1":
                highest_route = "L1"

        if highest_route in ["L1", "L2"]:
            next_status = CaseLifecycleStatus.APPROVAL_PENDING
            approval_status = "PENDING"
        else:
            next_status = CaseLifecycleStatus.RESOLVED
            approval_status = "NOT_REQUIRED"

        sar_req = agent_output.sar.file if agent_output.sar else False
        sar_status = "GENERATED" if sar_req else "NOT_REQUIRED"

        # 4. Update Case in Repository
        updated_data = {
            "status": next_status.value,
            "verdict": agent_output.case.verdict.value if hasattr(agent_output.case.verdict, "value") else str(agent_output.case.verdict),
            "fraud_probability": agent_output.case.fraud_probability,
            "fraud_pattern": agent_output.case.pattern.value if hasattr(agent_output.case.pattern, "value") else str(agent_output.case.pattern),
            "pattern_description": agent_output.case.pattern_description,
            "affected_txn_ids": agent_output.case.affected_txn_ids,
            "first_suspicious_txn_id": agent_output.case.first_suspicious_txn_id,
            "connected_card_ids": agent_output.case.connected_card_ids,
            "connected_device_profiles": agent_output.case.connected_device_profiles,
            "exposure_usd": agent_output.case.exposure_usd,
            "evidence": [e.model_dump() for e in agent_output.case.evidence],
            "similar_prior_cases": agent_output.case.similar_prior_cases,
            "evidence_requests": [r.model_dump() for r in agent_output.evidence_requests],
            "initial_next_best_action": [a.model_dump() for a in agent_output.next_best_actions.initial],
            "final_next_best_action": [a.model_dump() for a in agent_output.next_best_actions.final],
            "what_changed": agent_output.next_best_actions.what_changed,
            "approval_route": highest_route,
            "approval_status": approval_status,
            "summary": agent_output.case.summary,
            "stop_reason": agent_output.stop_reason,
            "sar_required": sar_req,
            "sar_status": sar_status,
            "sar_reference": agent_output.sar.model_dump() if agent_output.sar else None,
            "provenance": agent_output.provenance.model_dump() if hasattr(agent_output, "provenance") and agent_output.provenance else {
                "execution_mode": "OFFLINE_STAGED_SIMULATION",
                "graph_backend": "STAGED_DATASET",
                "graph_verified": False,
                "mcp_verified": False,
                "writeback_verified": False,
                "evidence_provenance": "LOCAL_STAGED_DATASET",
            },
        }

        persisted_case = self.repository.update_case(case_id, updated_data)

        # 5. Graph Writeback
        wb_res = self.writeback.write_case(persisted_case.model_dump())

        # 6. Graph Readback Verification
        rb_res = self.readback.verify_case(case_id)

        # 7. Update Case Memory
        if persisted_case.status in [CaseLifecycleStatus.RESOLVED, CaseLifecycleStatus.CLOSED]:
            self.memory_writer.register_case_in_memory(persisted_case.model_dump())

        AuditService.log_event(
            "INVESTIGATION_COMPLETED",
            case_id,
            "investigation_service",
            "SUCCESS",
            details={
                "verdict": persisted_case.verdict,
                "status": persisted_case.status.value,
                "writeback_status": rb_res.writeback_status,
                "approval_route": highest_route,
            },
        )

        return {
            "case_id": case_id,
            "status": persisted_case.status.value,
            "summary": persisted_case.summary,
            "verdict": persisted_case.verdict,
            "risk": {
                "fraud_probability": persisted_case.fraud_probability,
                "risk_score": persisted_case.risk_score,
            },
            "pattern": persisted_case.fraud_pattern,
            "next_best_action": persisted_case.final_next_best_action,
            "approval_route": persisted_case.approval_route,
            "approval_status": persisted_case.approval_status,
            "writeback_status": rb_res.writeback_status,
            "provenance": persisted_case.provenance,
        }

    def get_timeline(self, case_id: str) -> List[TimelineEvent]:
        if case_id in self._timelines:
            return self._timelines[case_id]
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")
        return TimelineBuilder.build_initial_timeline(case_id, case.trigger_type, case.trigger_text)
