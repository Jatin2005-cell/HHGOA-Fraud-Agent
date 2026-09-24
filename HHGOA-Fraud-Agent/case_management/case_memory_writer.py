"""Case Memory Writer: Extends the GraphRAG memory store with resolved DynamicCases."""

import os
import csv
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from .audit_service import AuditService


class CaseMemoryWriter:
    """Registers resolved DynamicCase investigations into the long-term investigation memory."""

    def __init__(self, processed_dir: Optional[str] = None):
        if not processed_dir:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            processed_dir = os.path.join(project_root, "dataset", "processed")
        self.processed_dir = processed_dir
        self.dynamic_memory_csv = os.path.join(self.processed_dir, "dynamic_case_memory.csv")
        self._ensure_memory_file()

    def _ensure_memory_file(self) -> None:
        if not os.path.exists(self.dynamic_memory_csv):
            with open(self.dynamic_memory_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "case_id", "customer_id", "card_id", "opened_at", "closed_at",
                    "outcome", "pattern", "first_fraud_txn_id", "n_txns",
                    "exposure_usd", "actions_taken", "report_filed", "analyst_notes"
                ])

    def register_case_in_memory(self, case_payload: Dict[str, Any]) -> bool:
        """
        Appends or updates a resolved DynamicCase record in the memory pool.
        Maintains separation from static ClosedCase historical records.
        """
        case_id = str(case_payload.get("case_id", "")).strip()
        if not case_id:
            return False

        # If already exists in dynamic memory, update it
        rows = []
        found = False
        if os.path.exists(self.dynamic_memory_csv):
            with open(self.dynamic_memory_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r.get("case_id") == case_id:
                        found = True
                        r["outcome"] = str(case_payload.get("verdict", "uncertain"))
                        r["pattern"] = str(case_payload.get("fraud_pattern", case_payload.get("pattern", "none")))
                        r["exposure_usd"] = str(case_payload.get("exposure_usd", 0.0))
                        r["analyst_notes"] = str(case_payload.get("summary", "")).replace("\n", " ")
                    rows.append(r)

        if not found:
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            actions_str = "; ".join([
                a.get("action", "") for a in case_payload.get("final_next_best_action", [])
            ])
            rows.append({
                "case_id": case_id,
                "customer_id": str(case_payload.get("customer_id", "")),
                "card_id": str(case_payload.get("card_id", "")),
                "opened_at": str(case_payload.get("created_at", now_str)),
                "closed_at": now_str,
                "outcome": str(case_payload.get("verdict", "uncertain")),
                "pattern": str(case_payload.get("fraud_pattern", case_payload.get("pattern", "none"))),
                "first_fraud_txn_id": str(case_payload.get("first_suspicious_txn_id", case_payload.get("flagged_txn_id", ""))),
                "n_txns": str(len(case_payload.get("affected_txn_ids", []))),
                "exposure_usd": str(case_payload.get("exposure_usd", 0.0)),
                "actions_taken": actions_str,
                "report_filed": str(case_payload.get("sar_required", False)),
                "analyst_notes": str(case_payload.get("summary", "")).replace("\n", " "),
            })

        with open(self.dynamic_memory_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "case_id", "customer_id", "card_id", "opened_at", "closed_at",
                "outcome", "pattern", "first_fraud_txn_id", "n_txns",
                "exposure_usd", "actions_taken", "report_filed", "analyst_notes"
            ])
            writer.writeheader()
            writer.writerows(rows)

        AuditService.log_event(
            operation="CASE_MEMORY_UPDATED",
            case_id=case_id,
            actor="memory_writer",
            status="SUCCESS",
            details={"case_id": case_id, "mode": "UPDATED" if found else "CREATED"},
        )
        return True
