"""Evidence API Routes."""

from fastapi import APIRouter, Depends
from typing import Any, Dict
from api.schemas.response_schemas import ApiResponse
from api.routes.investigations import evidence_service
from api.middleware.security import verify_api_security

router = APIRouter(prefix="/api/evidence", tags=["Evidence"], dependencies=[Depends(verify_api_security)])


@router.get("/{case_id}", response_model=ApiResponse[Dict[str, Any]])
def get_evidence_by_case(case_id: str):
    """Retrieves provenanced evidence claims and memory references for a case."""
    ev = evidence_service.get_evidence(case_id)
    return ApiResponse(success=True, data=ev, error=None)
