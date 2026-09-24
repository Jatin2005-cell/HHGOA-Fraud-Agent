"""Evidence Ranker: Normalizes, deduplicates, and ranks factual claims with strict provenance."""

from typing import Any, Dict, List
from agent.schemas.evidence_schema import EvidenceItem, EvidenceSourceEnum


class EvidenceRanker:
    """Ranks and filters evidence claims based on provenance, relevance, and factual strength."""

    SOURCE_WEIGHTS = {
        EvidenceSourceEnum.GRAPH: 1.0,
        EvidenceSourceEnum.CUSTOMER: 0.95,
        EvidenceSourceEnum.DOCUMENT: 0.85,
        EvidenceSourceEnum.EXTERNAL: 0.70,
    }

    @classmethod
    def rank_evidence(cls, evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Deduplicates and sorts evidence items by source authority and specificity."""
        seen_claims = set()
        unique_items = []
        for item in evidence_items:
            normalized_claim = " ".join(item.claim.strip().lower().split())
            if normalized_claim not in seen_claims:
                seen_claims.add(normalized_claim)
                unique_items.append(item)

        # Sort by source authority and number of anchor entity IDs
        unique_items.sort(
            key=lambda x: (
                cls.SOURCE_WEIGHTS.get(x.source, 0.5),
                len(x.entity_ids),
                len(x.claim),
            ),
            reverse=True,
        )
        return unique_items
