"""MCP Tools Adapter: Connects the AI Agent to the Phase 4 TigerGraph MCP Client.

Flow:
AI Agent -> agent/tools/mcp_tools.py -> Phase 4 investigation_mcp_client.py -> TigerGraph MCP -> GSQL -> TigerGraph
"""

import os
import sys
from typing import Any, Dict, List, Optional

import importlib.util

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
mcp_client_path = os.path.join(project_root, "mcp", "tools", "investigation_mcp_client.py")
if not os.path.exists(mcp_client_path):
    # Check parent workspace
    mcp_client_path = os.path.join(project_root, "..", "mcp", "tools", "investigation_mcp_client.py")

spec = importlib.util.spec_from_file_location("investigation_mcp_client", mcp_client_path)
mcp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_module)
TigerGraphMCPClient = mcp_module.TigerGraphMCPClient


class MCPInvestigationAdapter:
    """Thin adapter wrapping the verified Phase 4 TigerGraph MCP Client for the Agent."""

    def __init__(self, mcp_client: Optional[TigerGraphMCPClient] = None):
        self.mcp_client = mcp_client or TigerGraphMCPClient()

    def get_transaction_context(self, transaction_id: int) -> Dict[str, Any]:
        """Tool 1: Retrieves 360-degree dossier for target transaction."""
        return self.mcp_client.get_transaction_context(transaction_id)

    def get_card_transaction_window(self, card_id: str, center_ts: str, window_hours: int = 24) -> Dict[str, Any]:
        """Tool 2: Analyzes card velocity, micro-authorizations, and testing sequences."""
        return self.mcp_client.get_card_transaction_window(card_id, center_ts, window_hours)

    def find_device_neighbors(self, transaction_id: int) -> Dict[str, Any]:
        """Tool 3: Identifies shared device profiles and multi-card syndicates."""
        return self.mcp_client.find_device_neighbors(transaction_id)

    def find_region_anomalies(self, card_id: str, transaction_id: int) -> Dict[str, Any]:
        """Tool 4: Evaluates geographical dispersion and out-of-region card-present anomalies."""
        return self.mcp_client.find_region_anomalies(card_id, transaction_id)

    def find_similar_closed_cases(
        self,
        customer_id: Optional[str] = None,
        card_id: Optional[str] = None,
        pattern: Optional[str] = None,
        min_exposure: float = 0.0,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """Tool 5: Retrieves historical case memory from closed_cases_history."""
        return self.mcp_client.find_similar_closed_cases(
            customer_id=customer_id,
            card_id=card_id,
            pattern=pattern,
            min_exposure=min_exposure,
            max_results=max_results,
        )

    def get_customer_history(self, customer_id: str, max_txns: int = 50) -> Dict[str, Any]:
        """Tool 6: Retrieves customer baseline portfolio, total spend, and prior transaction history."""
        return self.mcp_client.get_customer_history(customer_id, max_txns)

    def find_connected_cards(self, card_id: str) -> Dict[str, Any]:
        """Tool 7: Discovers cards linked to the same customer or shared devices."""
        return self.mcp_client.find_connected_cards(card_id)

    def analyze_temporal_pattern(self, start_txn_id: int, max_hops: int = 5) -> Dict[str, Any]:
        """Tool 8: Analyzes consecutive transaction hop velocity, delta amounts, and structuring."""
        return self.mcp_client.analyze_temporal_pattern(start_txn_id, max_hops)

    def get_investigation_subgraph(self, transaction_id: int, max_siblings: int = 5) -> Dict[str, Any]:
        """Tool 9: Extracts local 2-hop neighborhood graph for GraphRAG context packaging."""
        return self.mcp_client.get_investigation_subgraph(transaction_id, max_siblings)
