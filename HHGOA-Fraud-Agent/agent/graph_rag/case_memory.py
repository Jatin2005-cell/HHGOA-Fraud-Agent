"""Historical Case Memory Store: Retrieves closed investigations from bank memory."""

import os
import pandas as pd
from typing import Any, Dict, List, Optional
from agent.schemas.evidence_schema import EvidenceItem, EvidenceSourceEnum


class CaseMemoryStore:
    """Provides memory retrieval across 5,565 closed cases (July-October 2016)."""

    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            # Fallback path finding
            possible_paths = [
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "processed", "closed_cases.csv")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "raw", "closed_cases_history.csv")),
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    data_path = p
                    break

        self.df = pd.read_csv(data_path) if data_path and os.path.exists(data_path) else pd.DataFrame()

    def search_similar_cases(
        self,
        customer_id: Optional[str] = None,
        card_id: Optional[str] = None,
        pattern: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Searches historical case records matching customer, card, or fraud pattern."""
        if self.df.empty:
            return []

        filt = self.df
        if customer_id and "customer_id" in filt.columns:
            matches = filt[filt["customer_id"] == customer_id]
            if not matches.empty:
                filt = matches
        if card_id and "card_id" in filt.columns:
            matches = filt[filt["card_id"] == card_id]
            if not matches.empty:
                filt = matches
        if pattern and pattern != "none" and "pattern" in filt.columns:
            matches = filt[filt["pattern"] == pattern]
            if not matches.empty:
                filt = matches

        results = []
        for _, row in filt.head(limit).iterrows():
            results.append({
                "case_id": str(row.get("case_id", "")),
                "customer_id": str(row.get("customer_id", "")),
                "card_id": str(row.get("card_id", "")),
                "outcome": str(row.get("outcome", "")),
                "pattern": str(row.get("pattern", "")),
                "first_fraud_txn_id": str(row.get("first_fraud_txn_id", "")),
                "exposure_usd": float(row.get("exposure_usd", 0.0)),
                "actions_taken": str(row.get("actions_taken", "")),
                "report_filed": bool(str(row.get("report_filed", "")).lower() in ["true", "1", "yes"]),
                "analyst_notes": str(row.get("analyst_notes", "")),
            })
        return results

    def get_evidence_claims(self, matched_cases: List[Dict[str, Any]]) -> List[EvidenceItem]:
        """Converts retrieved case memory into formal evidence items with source provenance."""
        evidence_items = []
        for c in matched_cases:
            case_id = c["case_id"]
            outcome = c["outcome"]
            pat = c["pattern"]
            notes = c["analyst_notes"]
            claim = (
                f"Historical precedent {case_id}: Closed investigation with outcome '{outcome}' "
                f"under pattern '{pat}'. Investigator notes: {notes}"
            )
            evidence_items.append(
                EvidenceItem(
                    claim=claim,
                    source=EvidenceSourceEnum.GRAPH,
                    ref=f"case_memory:{case_id}",
                    entity_ids=[case_id, c["customer_id"], c["card_id"]],
                )
            )
        return evidence_items
