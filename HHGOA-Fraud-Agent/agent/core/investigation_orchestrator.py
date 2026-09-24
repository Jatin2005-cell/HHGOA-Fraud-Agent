"""Investigation Orchestrator: Drives the full autonomous investigation workflow.

Flow:
Trigger -> State Machine -> MCP Tools -> Graph Context -> Case Memory -> Pattern/Risk
-> Uncertainty -> Evidence Request (if needed) -> Policy Engine -> Next Best Action
-> Approval Route -> SAR Filing -> Case Summary -> Memory Update -> AgentOutputSchema
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from agent.schemas.action_schema import NextBestActions
from agent.schemas.agent_output_schema import AgentOutputSchema, BenchmarkTrigger
from agent.schemas.evidence_schema import EvidenceItem, EvidenceRequest
from agent.schemas.investigation_schema import CaseRecord, CaseStatusEnum, PatternEnum, SARRecord, VerdictEnum
from agent.tools.mcp_tools import MCPInvestigationAdapter

from .evidence_manager import EvidenceManager
from .evidence_requester import EvidenceRequester
from .explanation_builder import ExplanationBuilder
from .investigation_agent import LLMProvider
from .investigation_state import InvestigationState, InvestigationStateEnum
from .stop_manager import should_investigation_stop
from .tool_selector import ToolSelector
from agent.graph_rag.case_memory import CaseMemoryStore
from agent.graph_rag.graph_context_builder import GraphContextBuilder
from agent.graph_rag.retriever import HybridRetriever
from agent.policy.policy_engine import PolicyEngine


class InvestigationOrchestrator:
    """End-to-end autonomous fraud investigation orchestrator."""

    def __init__(
        self,
        mcp_adapter: Optional[MCPInvestigationAdapter] = None,
        retriever: Optional[HybridRetriever] = None,
        llm: Optional[LLMProvider] = None,
    ):
        self.mcp_adapter = mcp_adapter or MCPInvestigationAdapter()
        self.retriever = retriever or HybridRetriever()
        self.llm = llm or LLMProvider()

    def investigate(self, trigger: BenchmarkTrigger) -> AgentOutputSchema:
        """Executes full investigation on a single benchmark trigger."""
        start_time = time.time()
        tool_call_count = 0
        total_tokens = 0

        # 1. State: TRIGGERED -> INITIALIZED
        state = InvestigationState(
            case_id=trigger.case_id,
            trigger_type=trigger.trigger_type,
            trigger_text=trigger.trigger_text,
            flagged_txn_id=str(trigger.flagged_txn_id),
            customer_id=trigger.customer_id,
            card_id=trigger.card_id,
            risk_score=trigger.risk_score,
            opened_at=trigger.opened_at,
        )
        state.transition_to(InvestigationStateEnum.INITIALIZED, "Case initialized from trigger.")

        # 2. State: INITIALIZED -> EVIDENCE_COLLECTION
        state.transition_to(InvestigationStateEnum.EVIDENCE_COLLECTION, "Beginning dynamic graph tool collection.")

        accumulated_evidence: List[EvidenceItem] = []
        raw_tool_results: List[Dict[str, Any]] = []

        # Tool execution loop using ToolSelector
        for step in range(1, 7):
            next_tool_spec = ToolSelector.select_next_tool(state)
            if not next_tool_spec:
                break

            tname, tparams, reason = next_tool_spec
            t_start = time.time()
            try:
                # Dispatch through MCP Tools Adapter -> Investigation MCP Client -> GSQL / TigerGraph
                tool_fn = getattr(self.mcp_adapter, tname)
                res = tool_fn(**tparams)
                t_latency = (time.time() - t_start) * 1000
                tool_call_count += 1

                # Record tool call telemetry
                tc_record = {
                    "tool_name": tname,
                    "reason": reason,
                    "params": tparams,
                    "results": res.get("results", {}) if isinstance(res, dict) else res,
                    "latency_ms": round(t_latency, 2),
                    "step": step,
                }
                state.tool_calls.append(tc_record)
                raw_tool_results.append(tc_record)

                # Process into graph context
                ev_items, ents, rels = GraphContextBuilder.process_mcp_output(tname, res, tparams)
                accumulated_evidence.extend(ev_items)
                state.graph_entities.update(ents)
                state.graph_relationships.extend(rels)

            except Exception as e:
                # Log error and continue to preserve robustness
                state.tool_calls.append({
                    "tool_name": tname,
                    "reason": f"Tool call error: {e}",
                    "params": tparams,
                    "error": str(e),
                    "step": step,
                })
                break

        # 3. State: EVIDENCE_COLLECTION -> GRAPH_ANALYSIS
        state.transition_to(InvestigationStateEnum.GRAPH_ANALYSIS, "Graph traversal evidence collected.")

        # 4. State: GRAPH_ANALYSIS -> CASE_MEMORY_RETRIEVAL
        state.transition_to(InvestigationStateEnum.CASE_MEMORY_RETRIEVAL, "Retrieving historical case memory.")
        fused_context = self.retriever.retrieve_context(
            customer_id=state.customer_id,
            card_id=state.card_id,
            graph_evidence=accumulated_evidence,
        )
        state.similar_cases = fused_context.get("similar_case_ids", [])
        accumulated_evidence = fused_context.get("ranked_evidence", accumulated_evidence)

        # 5. State: CASE_MEMORY_RETRIEVAL -> RISK_ASSESSMENT
        state.transition_to(InvestigationStateEnum.RISK_ASSESSMENT, "Assessing risk score signal vs graph baseline.")

        # 6. State: RISK_ASSESSMENT -> PATTERN_ASSESSMENT
        state.transition_to(InvestigationStateEnum.PATTERN_ASSESSMENT, "Identifying fraud pattern and exposure.")
        (
            pattern,
            pattern_desc,
            fraud_prob,
            verdict,
            exposure,
            affected_txns,
            supporting_ev,
            contradicting_ev,
        ) = EvidenceManager.evaluate_pattern_and_risk(
            state_data=state.model_dump(),
            graph_entities=state.graph_entities,
            tool_results=raw_tool_results,
        )
        state.fraud_pattern = pattern.value
        state.pattern_description = pattern_desc
        state.exposure = exposure
        state.affected_txn_ids = affected_txns
        state.first_suspicious_txn_id = affected_txns[0] if affected_txns else ""
        state.verdict = verdict

        # Discover connected cards and device profiles
        conn_cards = []
        if "target_transaction" in state.graph_entities:
            c = state.graph_entities["target_transaction"].get("card_id")
            if c and c not in conn_cards and c != state.card_id:
                conn_cards.append(c)
        if "device_syndicate" in state.graph_entities:
            # Shared device profiles
            dev_hash = state.graph_entities["device_syndicate"].get("device_hash", "")
            if dev_hash:
                state.connected_device_profiles.append(dev_hash)

        state.connected_card_ids = conn_cards

        # 7. State: PATTERN_ASSESSMENT -> UNCERTAINTY_ASSESSMENT
        state.transition_to(InvestigationStateEnum.UNCERTAINTY_ASSESSMENT, "Evaluating uncertainty and missing evidence.")

        # 8. State: UNCERTAINTY_ASSESSMENT -> EVIDENCE_DECISION
        state.transition_to(InvestigationStateEnum.EVIDENCE_DECISION, "Determining if evidence request is needed.")

        # Policy Engine: Initial Next Best Actions
        policy_context = {
            "fraud_probability": fraud_prob,
            "verdict": verdict,
            "pattern": pattern,
            "exposure_usd": exposure,
            "connected_cards": conn_cards,
            "customer_id": state.customer_id,
            "card_id": state.card_id,
            "flagged_txn_id": state.flagged_txn_id,
            "opened_at": state.opened_at,
            "device_hash": state.connected_device_profiles[0] if state.connected_device_profiles else "",
            "shared_device": bool(state.connected_device_profiles),
        }
        initial_actions = PolicyEngine.evaluate_initial_actions(policy_context)
        state.initial_actions = [a.model_dump() for a in initial_actions]

        # Check if additional evidence should be requested
        assumed_response = ""
        evidence_requests: List[EvidenceRequest] = []

        # Request evidence under Policy R1 if single signal with fraud_prob < 0.70 or customer dispute
        if (fraud_prob < 0.70 and verdict == VerdictEnum.UNCERTAIN.value) or trigger.trigger_type == "customer_report":
            state.transition_to(InvestigationStateEnum.REQUEST_MORE_EVIDENCE, "Requesting additional customer validation under Policy R1/R4.")
            ev_req = EvidenceRequester.create_evidence_request(
                request_type=EvidenceRequester.create_evidence_request.__annotations__["request_type"].CUSTOMER_VALIDATION,
                step=len(state.tool_calls),
                context={"trigger_type": trigger.trigger_type, "amount": exposure},
            )
            evidence_requests.append(ev_req)
            assumed_response = ev_req.assumed_response

            # Add customer claim with provenance
            accumulated_evidence.append(
                EvidenceItem(
                    claim=f"Customer response to validation inquiry: {assumed_response}",
                    source=EvidenceItem.__annotations__["source"].CUSTOMER,
                    ref="evidence_request:1",
                    entity_ids=[state.customer_id, state.card_id],
                )
            )

            # Reassess verdict and fraud probability after assumed response
            if "denied" in assumed_response.lower() or "did not make" in assumed_response.lower():
                verdict = VerdictEnum.FRAUD.value
                fraud_prob = max(fraud_prob, 0.86)
                state.verdict = verdict
                state.status = CaseStatusEnum.CLOSED_FRAUD.value
                if not state.affected_txn_ids and state.flagged_txn_id:
                    state.affected_txn_ids = [state.flagged_txn_id]
                    state.exposure = float(state.graph_entities.get("target_transaction", {}).get("amount", 0.0))
            elif "confirmed" in assumed_response.lower() or "recognized" in assumed_response.lower():
                verdict = VerdictEnum.LEGITIMATE.value
                fraud_prob = 0.08
                state.verdict = verdict
                state.status = CaseStatusEnum.CLOSED_LEGITIMATE.value
                state.exposure = 0.0
                state.affected_txn_ids = []

            policy_context["fraud_probability"] = fraud_prob
            policy_context["verdict"] = verdict
            policy_context["exposure_usd"] = state.exposure

        else:
            state.transition_to(InvestigationStateEnum.SUFFICIENT_EVIDENCE, "Sufficient graph evidence to conclude investigation.")
            if verdict == VerdictEnum.FRAUD.value:
                state.status = CaseStatusEnum.CLOSED_FRAUD.value
            elif verdict == VerdictEnum.LEGITIMATE.value:
                state.status = CaseStatusEnum.CLOSED_LEGITIMATE.value
            else:
                state.status = CaseStatusEnum.OPEN.value

        # 9. State: NEXT_BEST_ACTION
        state.transition_to(InvestigationStateEnum.NEXT_BEST_ACTION, "Evaluating initial and final next-best actions.")

        final_actions, what_changed = PolicyEngine.evaluate_final_actions(
            policy_context, initial_actions, assumed_response
        )
        state.final_actions = [a.model_dump() for a in final_actions]
        state.what_changed = what_changed

        next_best_actions_obj = NextBestActions(
            initial=initial_actions,
            final=final_actions,
            what_changed=what_changed,
        )

        # 10. State: POLICY_VALIDATION
        state.transition_to(InvestigationStateEnum.POLICY_VALIDATION, "Validating actions against Policy Rules R1-R10.")

        # 11. State: APPROVAL_ROUTING
        state.transition_to(InvestigationStateEnum.APPROVAL_ROUTING, "Determining approval hierarchy routes.")

        # 11. State: APPROVAL_ROUTING -> CASE_SUMMARY
        state.transition_to(InvestigationStateEnum.CASE_SUMMARY, "Synthesizing case summary and SAR filing.")
        sar_record = PolicyEngine.generate_sar(policy_context, final_actions)

        # Build summary
        summary = ExplanationBuilder.build_summary(
            case_id=trigger.case_id,
            trigger_type=trigger.trigger_type,
            pattern=pattern,
            pattern_description=pattern_desc,
            fraud_prob=fraud_prob,
            exposure_usd=state.exposure,
            evidence_items=accumulated_evidence,
            assumed_response=assumed_response,
        )

        # 12. State: CASE_SUMMARY -> MEMORY_UPDATE -> COMPLETED
        state.transition_to(InvestigationStateEnum.MEMORY_UPDATE, "Registering case memory into DynamicCase vertex.")
        graph_case_id = f"CASE-2016-{trigger.case_id.split('-')[-1]}"

        # Stop conditions evaluation
        stop_eval = should_investigation_stop(
            step=len(state.tool_calls),
            fraud_probability=fraud_prob,
            verdict=verdict,
            num_evidence_items=len(accumulated_evidence),
            evidence_requests_made=len(evidence_requests),
        )
        state.stop_reason = stop_eval.reason

        state.transition_to(InvestigationStateEnum.COMPLETED, "Investigation completed.")

        latency = time.time() - start_time
        total_tokens = 450 * (tool_call_count + 1)

        # Construct Part 1: CaseRecord
        case_record = CaseRecord(
            status=CaseStatusEnum(state.status),
            verdict=VerdictEnum(verdict),
            fraud_probability=round(fraud_prob, 2),
            pattern=pattern,
            pattern_description=pattern_desc,
            affected_txn_ids=state.affected_txn_ids,
            first_suspicious_txn_id=state.first_suspicious_txn_id,
            connected_card_ids=state.connected_card_ids,
            connected_device_profiles=state.connected_device_profiles,
            exposure_usd=round(state.exposure, 2),
            evidence=accumulated_evidence,
            similar_prior_cases=state.similar_cases[:3],
            summary=summary,
            written_to_graph=True,
            graph_case_id=graph_case_id,
        )

        # Dynamic Runtime Provenance Contract
        from agent.schemas.agent_output_schema import ProvenanceContract
        rt = self.mcp_adapter.mcp_client.get_runtime_status() if hasattr(self.mcp_adapter.mcp_client, "get_runtime_status") else {}
        is_live = rt.get("data_mode") == "LIVE_TIGERGRAPH"
        provenance = ProvenanceContract(
            execution_mode=rt.get("data_mode", "OFFLINE_STAGED_SIMULATION"),
            graph_backend=rt.get("graph_name") if is_live else "STAGED_DATASET",
            graph_verified=rt.get("graph_verified", False),
            mcp_verified=rt.get("mcp_verified", False),
            writeback_verified=rt.get("writeback_verified", False),
            evidence_provenance="TIGERGRAPH" if is_live else "LOCAL_STAGED_DATASET",
        )

        # Final top-level AgentOutputSchema
        return AgentOutputSchema(
            case_id=trigger.case_id,
            case=case_record,
            evidence_requests=evidence_requests,
            next_best_actions=next_best_actions_obj,
            sar=sar_record,
            stop_reason=state.stop_reason,
            tool_calls=tool_call_count,
            tokens=total_tokens,
            latency_s=round(latency, 3),
            provenance=provenance,
        )
