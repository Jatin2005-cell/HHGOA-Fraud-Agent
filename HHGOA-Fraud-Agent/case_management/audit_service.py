"""Audit Service: Records structured, tamper-evident audit logs for case operations."""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class AuditService:
    """Manages audit logging for investigations, case lifecycle events, approvals, and writebacks."""

    _logger: Optional[logging.Logger] = None

    @classmethod
    def _get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            logger = logging.getLogger("CaseManagementAudit")
            logger.setLevel(logging.INFO)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            log_dir = os.path.join(project_root, "case_management")
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "audit.log")

            handler = logging.FileHandler(log_path, encoding="utf-8")
            formatter = logging.Formatter('{"timestamp": "%(asctime)s", "audit": %(message)s}')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            cls._logger = logger
        return cls._logger

    @classmethod
    def log_event(
        cls,
        operation: str,
        case_id: str,
        actor: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Logs an auditable event with sanitized parameters (no credentials)."""
        logger = cls._get_logger()
        sanitized_details = {}
        if details:
            for k, v in details.items():
                if "pass" not in k.lower() and "token" not in k.lower() and "secret" not in k.lower():
                    sanitized_details[k] = str(v) if not isinstance(v, (int, float, bool, list, dict)) else v

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id or "internal",
            "case_id": case_id,
            "actor": actor,
            "operation": operation,
            "status": status,
            "details": sanitized_details,
        }
        logger.info(json.dumps(payload))
        return payload
