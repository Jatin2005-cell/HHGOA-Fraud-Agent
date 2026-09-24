"""Case Repository: Persistent storage and retrieval for DynamicCase entities."""

import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .case_lifecycle import CaseLifecycleStatus, CaseLifecycleManager


class DynamicCaseRecord(BaseModel):
    case_id: str
    status: CaseLifecycleStatus = CaseLifecycleStatus.NEW
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    trigger_type: str = "risk_score"
    trigger_text: str = ""

    flagged_txn_id: str = ""
    customer_id: str = ""
    card_id: str = ""

    verdict: str = "uncertain"
    fraud_probability: Optional[float] = None
    risk_score: Optional[float] = None

    fraud_pattern: str = "none"
    pattern_description: str = ""

    affected_txn_ids: List[str] = Field(default_factory=list)
    first_suspicious_txn_id: str = ""

    connected_card_ids: List[str] = Field(default_factory=list)
    connected_device_profiles: List[str] = Field(default_factory=list)

    exposure_usd: float = 0.0

    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    similar_prior_cases: List[str] = Field(default_factory=list)
    evidence_requests: List[Dict[str, Any]] = Field(default_factory=list)

    initial_next_best_action: List[Dict[str, Any]] = Field(default_factory=list)
    final_next_best_action: List[Dict[str, Any]] = Field(default_factory=list)
    what_changed: str = "nothing"

    approval_route: str = "auto"
    approval_status: str = "NOT_REQUIRED"  # NOT_REQUIRED | PENDING | APPROVED | REJECTED
    approval_details: Optional[Dict[str, Any]] = None

    policy_rules_triggered: List[str] = Field(default_factory=list)

    summary: str = ""
    explanation: str = ""

    sar_required: bool = False
    sar_status: str = "NOT_REQUIRED"  # NOT_REQUIRED | PENDING | GENERATED | REVIEW_REQUIRED
    sar_reference: Optional[Dict[str, Any]] = None

    stop_reason: str = ""
    agent_version: str = "1.0.0"
    investigation_version: str = "phase6-v1"
    provenance: Dict[str, Any] = Field(default_factory=lambda: {
        "execution_mode": "OFFLINE_STAGED_SIMULATION",
        "graph_backend": "STAGED_DATASET",
        "graph_verified": False,
        "mcp_verified": False,
        "writeback_verified": False,
        "evidence_provenance": "LOCAL_STAGED_DATASET",
    })


class CaseRepository:
    """Manages idempotent persistence, querying, and updating of DynamicCase records."""

    def __init__(self, storage_dir: Optional[str] = None):
        if not storage_dir:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            storage_dir = os.path.join(project_root, "data", "cases")
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self._memory_cache: Dict[str, DynamicCaseRecord] = {}
        self._load_existing_cases()

    def _load_existing_cases(self) -> None:
        """Loads all existing case files from disk into memory cache."""
        if not os.path.exists(self.storage_dir):
            return
        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(self.storage_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    case = DynamicCaseRecord.model_validate(data)
                    self._memory_cache[case.case_id] = case
                except Exception:
                    pass

    def _persist_to_disk(self, case: DynamicCaseRecord) -> None:
        fpath = os.path.join(self.storage_dir, f"{case.case_id}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(case.model_dump(), f, indent=2)

    def create_case(self, case_record: DynamicCaseRecord) -> DynamicCaseRecord:
        """Idempotently creates a new case record. Raises ValueError if case_id already exists."""
        if case_record.case_id in self._memory_cache:
            raise ValueError(f"Case {case_record.case_id} already exists. Use update_case or upsert_case.")
        self._memory_cache[case_record.case_id] = case_record
        self._persist_to_disk(case_record)
        return case_record

    def get_case(self, case_id: str) -> Optional[DynamicCaseRecord]:
        """Retrieves case record by ID."""
        return self._memory_cache.get(case_id)

    def update_case(self, case_id: str, updates: Dict[str, Any]) -> DynamicCaseRecord:
        """Updates an existing case after validating lifecycle transitions if status changes."""
        case = self.get_case(case_id)
        if not case:
            raise KeyError(f"Case {case_id} not found.")

        # If status is updated, validate lifecycle transition
        if "status" in updates and updates["status"]:
            new_status = CaseLifecycleStatus(updates["status"])
            CaseLifecycleManager.validate_transition(case.status, new_status)
            case.status = new_status

        for k, v in updates.items():
            if k not in ["case_id", "status"] and hasattr(case, k):
                setattr(case, k, v)

        case.updated_at = datetime.now(timezone.utc).isoformat()
        self._memory_cache[case_id] = case
        self._persist_to_disk(case)
        return case

    def upsert_case(self, case_record: DynamicCaseRecord) -> Tuple[DynamicCaseRecord, str]:
        """Idempotently creates or updates a case. Returns (case, 'created'|'updated'|'unchanged')."""
        if case_record.case_id not in self._memory_cache:
            self._memory_cache[case_record.case_id] = case_record
            self._persist_to_disk(case_record)
            return case_record, "created"

        existing = self._memory_cache[case_record.case_id]
        if existing.model_dump(exclude={"updated_at"}) == case_record.model_dump(exclude={"updated_at"}):
            return existing, "unchanged"

        case_record.updated_at = datetime.now(timezone.utc).isoformat()
        self._memory_cache[case_record.case_id] = case_record
        self._persist_to_disk(case_record)
        return case_record, "updated"

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
        """Lists and filters cases with pagination. page_size capped at 100."""
        page_size = min(max(1, page_size), 100)
        page = max(1, page)

        results = list(self._memory_cache.values())

        if status:
            results = [c for c in results if c.status.value == status.upper()]
        if pattern:
            results = [c for c in results if c.fraud_pattern.lower() == pattern.lower()]
        if customer_id:
            results = [c for c in results if c.customer_id == customer_id]
        if card_id:
            results = [c for c in results if c.card_id == card_id]
        if approval_status:
            results = [c for c in results if c.approval_status.upper() == approval_status.upper()]
        if sar_status:
            results = [c for c in results if c.sar_status.upper() == sar_status.upper()]
        if risk_level:
            if risk_level.upper() == "HIGH":
                results = [c for c in results if (c.fraud_probability or 0.0) >= 0.70]
            elif risk_level.upper() == "MEDIUM":
                results = [c for c in results if 0.30 <= (c.fraud_probability or 0.0) < 0.70]
            elif risk_level.upper() == "LOW":
                results = [c for c in results if (c.fraud_probability or 0.0) < 0.30]

        total = len(results)
        # Sort by updated_at descending
        results.sort(key=lambda c: c.updated_at, reverse=True)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return results[start_idx:end_idx], total
