"""Evidence Service: Extracts provenanced claims for an investigation case."""

from typing import Any, Dict, List, Optional
from case_management.case_repository import CaseRepository


class EvidenceService:
    def __init__(self, repository: Optional[CaseRepository] = None):
        self.repository = repository or CaseRepository()

    def get_evidence(self, case_id: str) -> Dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        return {
            "case_id": case.case_id,
            "total_claims": len(case.evidence),
            "evidence": case.evidence,
            "similar_prior_cases": case.similar_prior_cases,
        }
