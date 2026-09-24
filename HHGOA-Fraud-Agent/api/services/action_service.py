"""Action Service: Extracts initial and final actions and what changed."""

from typing import Any, Dict, Optional
from case_management.case_repository import CaseRepository


class ActionService:
    def __init__(self, repository: Optional[CaseRepository] = None):
        self.repository = repository or CaseRepository()

    def get_actions(self, case_id: str) -> Dict[str, Any]:
        case = self.repository.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        return {
            "case_id": case.case_id,
            "initial_actions": case.initial_next_best_action,
            "final_actions": case.final_next_best_action,
            "what_changed": case.what_changed,
            "approval_route": case.approval_route,
            "approval_status": case.approval_status,
        }
