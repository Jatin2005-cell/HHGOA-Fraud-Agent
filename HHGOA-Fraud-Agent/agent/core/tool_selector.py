"""Intelligent Tool Selection for Fraud Investigation Agent.

Selects the most informative TigerGraph MCP tool based on current investigation state,
avoiding unnecessary or redundant tool invocations.
"""

from typing import Any, Dict, List, Optional, Tuple
from .investigation_state import InvestigationState


class ToolSelector:
    """Evaluates investigation evidence and selects the next best tool with internal reasoning."""

    @staticmethod
    def select_next_tool(state: InvestigationState) -> Optional[Tuple[str, Dict[str, Any], str]]:
        """
        Returns:
            Tuple of (tool_name, tool_inputs, reason) or None if evidence collection should stop.
        """
        called_tools = {tc["tool_name"] for tc in state.tool_calls}
        
        # Step 1: Always anchor on transaction context first
        if "get_transaction_context" not in called_tools:
            return (
                "get_transaction_context",
                {"transaction_id": int(state.flagged_txn_id)},
                "Retrieve foundational transaction context, cardholder anchor, channel, and direct connections.",
            )

        txn_ctx = state.graph_entities.get("target_transaction", {})
        channel = txn_ctx.get("channel", "online")
        card_id = state.card_id or txn_ctx.get("card_id", "")
        customer_id = state.customer_id or txn_ctx.get("customer_id", "")
        txn_ts = txn_ctx.get("ts", "")
        amt = float(txn_ctx.get("amount", 0.0))

        # Step 2: Online channel analysis
        if channel == "online":
            # Shared device syndicates check
            if "find_device_neighbors" not in called_tools:
                return (
                    "find_device_neighbors",
                    {"transaction_id": int(state.flagged_txn_id)},
                    "Online transaction: check device profile for multi-card syndicates or shared fraud rings.",
                )

            # Card velocity and testing sequence check
            if "get_card_transaction_window" not in called_tools and card_id and txn_ts:
                return (
                    "get_card_transaction_window",
                    {"card_id": card_id, "center_ts": txn_ts, "window_hours": 24},
                    "Evaluate 24h card activity for micro-authorizations (<$5) or rapid velocity bursts.",
                )

        # Step 3: In-person channel analysis
        if channel == "in_person":
            if "find_region_anomalies" not in called_tools and card_id:
                return (
                    "find_region_anomalies",
                    {"card_id": card_id, "transaction_id": int(state.flagged_txn_id)},
                    "In-person transaction: verify billing region distribution against cardholder home region.",
                )

        # Step 4: Customer spending baseline check
        if "get_customer_history" not in called_tools and customer_id:
            # Triggered if amount is significant or customer report is disputed
            if amt >= 100.0 or state.trigger_type in ["customer_report", "analyst_request"] or len(state.tool_calls) < 3:
                return (
                    "get_customer_history",
                    {"customer_id": customer_id, "max_txns": 50},
                    "Establish customer spend baseline, total cards owned, and normal activity profile.",
                )

        # Step 5: Connected cards analysis
        if "find_connected_cards" not in called_tools and card_id:
            return (
                "find_connected_cards",
                {"card_id": card_id},
                "Check for other cards held by customer to evaluate customer-wide exposure or multi-card breach.",
            )

        # Step 6: Temporal chaining / structuring check
        if "analyze_temporal_pattern" not in called_tools and len(state.tool_calls) < 5:
            if amt in [470.0, 480.0, 490.0, 482.12] or state.fraud_pattern in ["card_testing", "threshold_avoidance", "undocumented"]:
                return (
                    "analyze_temporal_pattern",
                    {"start_txn_id": int(state.flagged_txn_id), "max_hops": 5},
                    "Check consecutive transactions along NEXT_TRANSACTION edge for structuring or rapid cycling.",
                )

        # Step 7: Historical Case Memory search
        if "find_similar_closed_cases" not in called_tools:
            return (
                "find_similar_closed_cases",
                {"customer_id": customer_id, "max_results": 10},
                "Retrieve historical bank precedent from closed cases for this customer and similar patterns.",
            )

        # All necessary tools have been strategically executed
        return None
