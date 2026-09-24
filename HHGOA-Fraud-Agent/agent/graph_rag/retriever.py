"""Hybrid Retriever: Unifies graph evidence, policy rules, and historical memory."""

from typing import Any, Dict, List, Optional
from agent.schemas.evidence_schema import EvidenceItem, EvidenceSourceEnum
from .document_store import DocumentStore
from .case_memory import CaseMemoryStore
from .evidence_ranker import EvidenceRanker


class HybridRetriever:
    """Retrieves and integrates graph context, historical memory, and policy documents."""

    def __init__(self, memory_store: Optional[CaseMemoryStore] = None):
        self.memory_store = memory_store or CaseMemoryStore()
        self.doc_store = DocumentStore

    def retrieve_context(
        self,
        customer_id: Optional[str] = None,
        card_id: Optional[str] = None,
        pattern_hypothesis: Optional[str] = None,
        graph_evidence: Optional[List[EvidenceItem]] = None,
    ) -> Dict[str, Any]:
        """Retrieves and fuses all relevant context for agent reasoning."""
        # 1. Historical Cases
        similar_cases = self.memory_store.search_similar_cases(
            customer_id=customer_id,
            card_id=card_id,
            pattern=pattern_hypothesis,
            limit=5,
        )
        case_evidence = self.memory_store.get_evidence_claims(similar_cases)

        # 2. Pattern definition
        pattern_info = self.doc_store.get_pattern_info(pattern_hypothesis or "none")

        # 3. Combine and rank evidence
        all_evidence = (graph_evidence or []) + case_evidence
        ranked_evidence = EvidenceRanker.rank_evidence(all_evidence)

        # 4. Applicable Policy Rules
        applicable_rules = self.doc_store.get_all_policy_rules()

        return {
            "similar_cases": similar_cases,
            "similar_case_ids": [c["case_id"] for c in similar_cases],
            "pattern_info": pattern_info,
            "ranked_evidence": ranked_evidence,
            "policy_rules": applicable_rules,
        }
