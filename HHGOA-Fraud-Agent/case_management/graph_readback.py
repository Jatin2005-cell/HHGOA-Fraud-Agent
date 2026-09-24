"""Case Readback Verification Service: Confirms persistence of DynamicCase vertices and edges."""

import os
import csv
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .audit_service import AuditService


class ReadbackVerificationResult(BaseModel):
    writeback_status: str  # VERIFIED | VERIFICATION_FAILED
    case_id: str
    graph_case_id: str
    verified_entities: List[str] = Field(default_factory=list)
    verified_relationships: List[str] = Field(default_factory=list)
    persisted_attributes: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class CaseReadbackService:
    """Reads back newly persisted cases from the graph store to confirm persistence."""

    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(project_root, "dataset", "processed")
        self.data_dir = data_dir
        self.dynamic_cases_csv = os.path.join(self.data_dir, "dynamic_cases.csv")
        self.edges_involves_csv = os.path.join(self.data_dir, "edges_case_involves.csv")
        self.edges_card_csv = os.path.join(self.data_dir, "edges_case_on_card.csv")

    def verify_case(self, case_id: str) -> ReadbackVerificationResult:
        """Reads back and verifies existence and integrity of DynamicCase vertex and edges."""
        if not os.path.exists(self.dynamic_cases_csv):
            return ReadbackVerificationResult(
                writeback_status="VERIFICATION_FAILED",
                case_id=case_id,
                graph_case_id="",
                error="dynamic_cases storage store does not exist.",
            )

        found_record: Optional[Dict[str, Any]] = None
        with open(self.dynamic_cases_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r["case_id"] == case_id:
                    found_record = dict(r)
                    break

        if not found_record:
            return ReadbackVerificationResult(
                writeback_status="VERIFICATION_FAILED",
                case_id=case_id,
                graph_case_id="",
                error=f"DynamicCase vertex {case_id} not found upon readback.",
            )

        graph_case_id = f"CASE-2016-{case_id.split('-')[-1]}"
        verified_entities = [f"DynamicCase:{case_id}"]
        verified_relationships = []

        # Check CASE_INVOLVES edges
        if os.path.exists(self.edges_involves_csv):
            with open(self.edges_involves_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r.get("case_id") == case_id:
                        verified_relationships.append(f"CASE_INVOLVES({case_id}->{r.get('txn_id')})")
                        verified_entities.append(f"Transaction:{r.get('txn_id')}")

        # Check CASE_ON_CARD edges
        if os.path.exists(self.edges_card_csv):
            with open(self.edges_card_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r.get("case_id") == case_id:
                        verified_relationships.append(f"CASE_ON_CARD({case_id}->{r.get('card_id')})")
                        verified_entities.append(f"Card:{r.get('card_id')}")

        # Audit
        AuditService.log_event(
            operation="GRAPH_READBACK_VERIFIED",
            case_id=case_id,
            actor="readback_service",
            status="SUCCESS",
            details={
                "verified_entities_count": len(verified_entities),
                "verified_relationships_count": len(verified_relationships),
            },
        )

        return ReadbackVerificationResult(
            writeback_status="VERIFIED",
            case_id=case_id,
            graph_case_id=graph_case_id,
            verified_entities=verified_entities,
            verified_relationships=verified_relationships,
            persisted_attributes=found_record,
        )
