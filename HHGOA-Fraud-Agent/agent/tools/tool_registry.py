"""Tool Registry and Metadata for Agent Investigation Tools."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    name: str
    purpose: str
    required_inputs: List[str]
    optional_inputs: List[str] = Field(default_factory=list)
    evidence_returned: str
    latency_tier: str = "fast"  # fast (< 50ms) | moderate (< 500ms) | heavy (< 2s)
    when_to_use: str
    when_not_to_use: str


TOOL_METADATA_REGISTRY: Dict[str, ToolMetadata] = {
    "get_transaction_context": ToolMetadata(
        name="get_transaction_context",
        purpose="Retrieve primary 360-degree context for the flagged transaction (card, customer, amount, channel, device).",
        required_inputs=["transaction_id"],
        evidence_returned="Transaction metadata, customer ID, card ID, device hash, billing region, direct case links.",
        latency_tier="fast",
        when_to_use="Always call first on any investigation trigger to establish baseline entity anchors.",
        when_not_to_use="Do not call if transaction details have already been retrieved.",
    ),
    "get_card_transaction_window": ToolMetadata(
        name="get_card_transaction_window",
        purpose="Inspect transactions within a +/- window around the target to spot velocity surges or card testing.",
        required_inputs=["card_id", "center_ts"],
        optional_inputs=["window_hours"],
        evidence_returned="Micro-authorizations (< $5), peak amount, velocity spike count, testing sequence flag.",
        latency_tier="moderate",
        when_to_use="Use when card testing, burst authorizations, or velocity compromise is suspected.",
        when_not_to_use="Do not call if the alert is solely about an out-of-region card-present transaction with normal frequency.",
    ),
    "find_device_neighbors": ToolMetadata(
        name="find_device_neighbors",
        purpose="Traverse from transaction to DeviceProfile to identify other cards and customers sharing the device.",
        required_inputs=["transaction_id"],
        evidence_returned="Device hardware/OS specs, connected cards count, connected customers count, linked fraud cases.",
        latency_tier="moderate",
        when_to_use="Use for online transactions to check if device is tied to a shared syndicate or multi-card fraud ring.",
        when_not_to_use="Do not call for in-person transactions (ProductCD == 'W') as they have no device record.",
    ),
    "find_region_anomalies": ToolMetadata(
        name="find_region_anomalies",
        purpose="Analyze historical in-person billing region distribution to assess out-of-region anomalies.",
        required_inputs=["card_id", "transaction_id"],
        evidence_returned="Historical region distribution, home region ratio, whether flagged region is completely novel.",
        latency_tier="moderate",
        when_to_use="Use when trigger involves an in-person charge in an unfamiliar billing region (addr1).",
        when_not_to_use="Do not call for pure online (e-commerce) transactions where physical location is addr1 billing only.",
    ),
    "find_similar_closed_cases": ToolMetadata(
        name="find_similar_closed_cases",
        purpose="Retrieve historical case memory from closed_cases_history for pattern precedence and prior outcomes.",
        required_inputs=[],
        optional_inputs=["customer_id", "card_id", "pattern", "min_exposure", "max_results"],
        evidence_returned="Precedent closed case records: outcome, pattern, actions taken, notes, exposure.",
        latency_tier="fast",
        when_to_use="Use when evaluating pattern hypotheses against bank memory or checking if customer/card has prior cases.",
        when_not_to_use="Do not call if no preliminary pattern or customer anchor has been established yet.",
    ),
    "get_customer_history": ToolMetadata(
        name="get_customer_history",
        purpose="Retrieve customer baseline spend, total cards owned, and normal activity profile.",
        required_inputs=["customer_id"],
        optional_inputs=["max_txns"],
        evidence_returned="Total customer cards, total lifetime spend, average transaction amount, recent transaction sample.",
        latency_tier="fast",
        when_to_use="Use when assessing account takeover or deciding whether transaction amount is an anomaly for this customer.",
        when_not_to_use="Do not call if single-card compromise is already confirmed by testing sequence.",
    ),
    "find_connected_cards": ToolMetadata(
        name="find_connected_cards",
        purpose="Discover adjacent cards owned by the same customer or linked via shared devices.",
        required_inputs=["card_id"],
        evidence_returned="List of other card IDs belonging to customer or connected in the graph.",
        latency_tier="fast",
        when_to_use="Use when considering BLOCK_ALL_CARDS, MONITOR_CONNECTED_CARDS, or evaluating customer-wide exposure.",
        when_not_to_use="Do not call if customer owns only one card.",
    ),
    "analyze_temporal_pattern": ToolMetadata(
        name="analyze_temporal_pattern",
        purpose="Follow forward NEXT_TRANSACTION edges to analyze consecutive inter-transaction deltas and structuring.",
        required_inputs=["start_txn_id"],
        optional_inputs=["max_hops"],
        evidence_returned="Sequence of subsequent transactions, delta seconds, delta amounts, structuring indicator.",
        latency_tier="moderate",
        when_to_use="Use when rapid-fire consecutive purchases, structuring ($470-$499), or fast cashout is suspected.",
        when_not_to_use="Do not call for isolated, single-transaction alerts with long inter-transaction gaps.",
    ),
    "get_investigation_subgraph": ToolMetadata(
        name="get_investigation_subgraph",
        purpose="Extract 2-hop local graph neighborhood around transaction for GraphRAG context packaging.",
        required_inputs=["transaction_id"],
        optional_inputs=["max_siblings"],
        evidence_returned="Local graph entities (card, customer, device, region, connected cases) and their relations.",
        latency_tier="moderate",
        when_to_use="Use during GraphRAG graph context synthesis to build complete structured neighborhood evidence.",
        when_not_to_use="Do not call repeatedly if already fetched in the initial step.",
    ),
}


class ToolRegistry:
    """Registry providing metadata and execution wrapper for investigation tools."""

    @staticmethod
    def get_tool_metadata(tool_name: str) -> Optional[ToolMetadata]:
        return TOOL_METADATA_REGISTRY.get(tool_name)

    @staticmethod
    def list_tools() -> List[ToolMetadata]:
        return list(TOOL_METADATA_REGISTRY.values())
