"""SAR Service: Generates, retrieves, and validates SAR records."""

from typing import Any, Dict, Optional
from case_management.case_repository import CaseRepository
from sar.sar_generator import SARGenerator, GeneratedSAR
from sar.sar_validator import SARValidator


class SARService:
    def __init__(self, repository: Optional[CaseRepository] = None):
        self.repository = repository or CaseRepository()

    def get_sar(self, case_id: str) -> Dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        if case.sar_reference:
            ref = dict(case.sar_reference)
            ref["case_id"] = case_id
            ref["status"] = case.sar_status
            return ref

        # Generate on the fly if needed
        generated = SARGenerator.generate_for_case(case.model_dump())
        return {
            "case_id": case.case_id,
            "file": generated.file,
            "reason": generated.reason,
            "narrative": generated.narrative,
            "subjects": generated.subjects,
            "total_amount_usd": generated.total_amount_usd,
            "activity_dates": generated.activity_dates,
            "status": generated.status,
        }
