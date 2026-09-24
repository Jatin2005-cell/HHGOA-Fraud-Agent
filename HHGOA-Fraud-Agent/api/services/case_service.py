"""Case Service: Business logic for case retrieval and filtering."""

from typing import Any, Dict, List, Optional, Tuple
from case_management.case_repository import CaseRepository, DynamicCaseRecord
from case_management.case_lifecycle import CaseLifecycleStatus
from case_management.timeline_builder import TimelineBuilder, TimelineEvent


class CaseService:
    def __init__(self, repository: Optional[CaseRepository] = None):
        self.repository = repository or CaseRepository()

    def get_case(self, case_id: str) -> DynamicCaseRecord:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")
        return case

    def list_cases(
        self,
        status: Optional[str] = None,
        pattern: Optional[str] = None,
        customer_id: Optional[str] = None,
        card_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        approval_status: Optional[str] = None,
        sar_status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[DynamicCaseRecord], int]:
        return self.repository.list_cases(
            status=status,
            pattern=pattern,
            customer_id=customer_id,
            card_id=card_id,
            risk_level=risk_level,
            approval_status=approval_status,
            sar_status=sar_status,
            page=page,
            page_size=page_size,
        )

    def get_timeline(self, case_id: str) -> List[TimelineEvent]:
        case = self.get_case(case_id)
        # Construct timeline based on current case state and history
        return TimelineBuilder.build_initial_timeline(
            case_id=case.case_id,
            trigger_type=case.trigger_type,
            trigger_text=case.trigger_text,
        )
