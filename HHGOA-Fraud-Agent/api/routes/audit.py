"""Audit log API routes."""

import os
import json
from fastapi import APIRouter, Depends, Query
from typing import Any, Dict, List, Optional

from api.schemas.response_schemas import ApiResponse
from api.middleware.security import verify_api_security

router = APIRouter(prefix="/api/audit", tags=["Audit"], dependencies=[Depends(verify_api_security)])


@router.get("", response_model=ApiResponse[Dict[str, Any]])
def list_audit_logs(
    case_id: Optional[str] = Query(None, description="Filter by Case ID"),
    operation: Optional[str] = Query(None, description="Filter by operation name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Retrieves paginated audit events from the immutable audit trail."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    log_path = os.path.join(project_root, "case_management", "audit.log")

    events: List[Dict[str, Any]] = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    # Extract audit payload
                    audit_entry = obj.get("audit", obj)
                    if isinstance(audit_entry, str):
                        audit_entry = json.loads(audit_entry)

                    if case_id and case_id.lower() not in str(audit_entry.get("case_id", "")).lower():
                        continue
                    if operation and operation.lower() not in str(audit_entry.get("operation", "")).lower():
                        continue

                    events.append(audit_entry)
                except Exception:
                    continue

    events.reverse()  # Newest first
    total = len(events)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = events[start:end]

    return ApiResponse(
        success=True,
        data={"items": paginated, "total": total, "page": page, "page_size": page_size},
        error=None,
    )
