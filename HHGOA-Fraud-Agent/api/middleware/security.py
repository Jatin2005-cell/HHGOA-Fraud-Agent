"""Security middleware and API Token Authentication abstraction."""

import re
from fastapi import Header, HTTPException, Security
from api.config import settings

# Injection prevention regex
DESTRUCTIVE_GSQL_RE = re.compile(r"\b(DROP|CLEAR|DELETE|TRUNCATE|ALTER)\b", re.IGNORECASE)


def verify_api_security(authorization: str = Header(None)) -> bool:
    """Verifies Bearer token if API_AUTH_ENABLED is True."""
    if not settings.API_AUTH_ENABLED:
        return True

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Missing Authorization header."},
        )

    token = authorization.replace("Bearer ", "").strip()
    if token != settings.API_AUTH_TOKEN:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Invalid API authentication token."},
        )

    return True


def sanitize_input_string(val: str) -> str:
    """Sanitizes user input strings to prevent SQL/GSQL or prompt injection."""
    if DESTRUCTIVE_GSQL_RE.search(val):
        raise ValueError("Destructive database keywords detected in input string.")
    return val.strip()
