"""Unit tests for GraphRAG context building, ranking, and memory retrieval."""

from agent.schemas.evidence_schema import EvidenceItem, EvidenceSourceEnum
from agent.graph_rag.document_store import DocumentStore
from agent.graph_rag.evidence_ranker import EvidenceRanker
from agent.graph_rag.case_memory import CaseMemoryStore
from agent.graph_rag.retriever import HybridRetriever


def test_document_store():
    rule_r1 = DocumentStore.get_policy_rule("R1")
    assert rule_r1 is not None
    assert "Verify before you block" in rule_r1["title"]
    assert "VERIFY_WITH_CUSTOMER" in rule_r1["actions"]


def test_evidence_ranker():
    e1 = EvidenceItem(
        claim="Graph traversal confirmed shared device profile.",
        source=EvidenceSourceEnum.GRAPH,
        ref="query:device_neighbors_query",
        entity_ids=["DEV_123"],
    )
    e2 = EvidenceItem(
        claim="Document reference for R1 policy.",
        source=EvidenceSourceEnum.DOCUMENT,
        ref="doc:R1",
        entity_ids=[],
    )
    ranked = EvidenceRanker.rank_evidence([e2, e1])
    # Graph evidence has higher weight (1.0 vs 0.85)
    assert ranked[0].source == EvidenceSourceEnum.GRAPH


def test_case_memory_retrieval():
    mem = CaseMemoryStore()
    matches = mem.search_similar_cases(limit=3)
    assert len(matches) > 0
    claims = mem.get_evidence_claims(matches)
    assert len(claims) == len(matches)
    assert claims[0].source == EvidenceSourceEnum.GRAPH


if __name__ == "__main__":
    test_document_store()
    test_evidence_ranker()
    test_case_memory_retrieval()
    print("test_graph_rag.py: ALL PASS")
