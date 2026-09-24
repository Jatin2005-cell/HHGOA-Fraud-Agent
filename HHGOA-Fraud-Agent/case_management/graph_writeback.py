"""Isolated Case Writeback Service: Safely and idempotently mutates DynamicCase vertices and edges.

IMPORTANT:
Maintains complete separation from the Phase 4 Read-Only Investigation MCP layer.
Does NOT permit arbitrary GSQL or destructive database operations.
"""

import os
import re
import csv
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .audit_service import AuditService


class WritebackResult(BaseModel):
    success: bool
    case_id: str
    graph_case_id: str
    status: str  # CREATED | UPDATED | UNCHANGED | FAILED
    vertices_written: List[str] = Field(default_factory=list)
    edges_written: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class CaseWritebackService:
    """Safe, idempotent writeback service for TigerGraph DynamicCase vertices and edges."""

    # Validation regexes
    CASE_ID_RE = re.compile(r"^(HHG-\d{3}|CASE-\d{4}-\d+)$")
    CARD_ID_RE = re.compile(r"^C\d{5}-K\d+$")
    TXN_ID_RE = re.compile(r"^\d{7}$")

    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(project_root, "dataset", "processed")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.dynamic_cases_csv = os.path.join(self.data_dir, "dynamic_cases.csv")
        self._ensure_storage_tables()

    def _ensure_storage_tables(self) -> None:
        """Ensures dynamic_cases table and edge files exist with required schema headers."""
        if not os.path.exists(self.dynamic_cases_csv):
            with open(self.dynamic_cases_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "case_id", "opened_at", "closed_at", "status", "verdict",
                    "fraud_probability", "pattern", "pattern_description",
                    "exposure_usd", "stop_reason", "sar_filed", "summary"
                ])

    def write_case(self, case_payload: Dict[str, Any]) -> WritebackResult:
        """
        Idempotently writes or updates a DynamicCase vertex and associated graph edges.
        Validates entity formats and strictly prevents arbitrary mutations.
        """
        case_id = str(case_payload.get("case_id", "")).strip()
        if not self.CASE_ID_RE.match(case_id):
            return WritebackResult(
                success=False,
                case_id=case_id,
                graph_case_id="",
                status="FAILED",
                error=f"Invalid case_id format: {case_id}",
            )

        flagged_txn = str(case_payload.get("flagged_txn_id", "")).strip()
        card_id = str(case_payload.get("card_id", "")).strip()

        # Sanitize text
        summary = str(case_payload.get("summary", "")).replace("\n", " ").replace("\r", " ")
        pattern_desc = str(case_payload.get("pattern_description", "")).replace("\n", " ").replace("\r", " ")
        stop_reason = str(case_payload.get("stop_reason", "")).replace("\n", " ").replace("\r", " ")
        pattern = str(case_payload.get("pattern", case_payload.get("fraud_pattern", "none")))
        status = str(case_payload.get("status", "NEW"))
        verdict = str(case_payload.get("verdict", "uncertain"))
        sar_filed = bool(case_payload.get("sar_required") or (case_payload.get("sar_status") == "GENERATED"))
        fraud_prob = float(case_payload.get("fraud_probability") or 0.0)
        exposure = float(case_payload.get("exposure_usd") or 0.0)
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        graph_case_id = f"CASE-2016-{case_id.split('-')[-1]}"

        # 1. Update/Append to dynamic_cases.csv
        rows = []
        found = False
        if os.path.exists(self.dynamic_cases_csv):
            with open(self.dynamic_cases_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r["case_id"] == case_id:
                        found = True
                        r["status"] = status
                        r["verdict"] = verdict
                        r["fraud_probability"] = str(fraud_prob)
                        r["pattern"] = pattern
                        r["pattern_description"] = pattern_desc
                        r["exposure_usd"] = str(exposure)
                        r["stop_reason"] = stop_reason
                        r["sar_filed"] = str(sar_filed)
                        r["summary"] = summary
                        r["closed_at"] = now_str
                    rows.append(r)

        mutation_status = "UPDATED" if found else "CREATED"

        if not found:
            rows.append({
                "case_id": case_id,
                "opened_at": now_str,
                "closed_at": now_str,
                "status": status,
                "verdict": verdict,
                "fraud_probability": str(fraud_prob),
                "pattern": pattern,
                "pattern_description": pattern_desc,
                "exposure_usd": str(exposure),
                "stop_reason": stop_reason,
                "sar_filed": str(sar_filed),
                "summary": summary,
            })

        with open(self.dynamic_cases_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "case_id", "opened_at", "closed_at", "status", "verdict",
                "fraud_probability", "pattern", "pattern_description",
                "exposure_usd", "stop_reason", "sar_filed", "summary"
            ])
            writer.writeheader()
            writer.writerows(rows)

        vertices_written = [f"DynamicCase:{case_id}"]
        edges_written = []

        # 2. Write CASE_INVOLVES edge
        if flagged_txn and self.TXN_ID_RE.match(flagged_txn):
            involves_path = os.path.join(self.data_dir, "edges_case_involves.csv")
            edge_exists = False
            if os.path.exists(involves_path):
                with open(involves_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if r.get("case_id") == case_id and r.get("txn_id") == flagged_txn:
                            edge_exists = True
                            break
            if not edge_exists:
                with open(involves_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([case_id, flagged_txn, "true", "true"])
                edges_written.append(f"CASE_INVOLVES({case_id}->{flagged_txn})")

        # 3. Write CASE_ON_CARD edge
        if card_id and self.CARD_ID_RE.match(card_id):
            card_edge_path = os.path.join(self.data_dir, "edges_case_on_card.csv")
            card_edge_exists = False
            if os.path.exists(card_edge_path):
                with open(card_edge_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if r.get("case_id") == case_id and r.get("card_id") == card_id:
                            card_edge_exists = True
                            break
            if not card_edge_exists:
                with open(card_edge_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([case_id, card_id])
                edges_written.append(f"CASE_ON_CARD({case_id}->{card_id})")

        # Audit
        AuditService.log_event(
            operation="GRAPH_WRITEBACK",
            case_id=case_id,
            actor="writeback_service",
            status="SUCCESS",
            details={
                "mutation_status": mutation_status,
                "vertices_written": vertices_written,
                "edges_written": edges_written,
                "exposure": exposure,
            },
        )

        return WritebackResult(
            success=True,
            case_id=case_id,
            graph_case_id=graph_case_id,
            status=mutation_status,
            vertices_written=vertices_written,
            edges_written=edges_written,
        )
