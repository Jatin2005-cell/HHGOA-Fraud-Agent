"""SAR API Routes."""

from fastapi import APIRouter, Depends
from typing import Any, Dict
from api.schemas.response_schemas import ApiResponse
from api.routes.investigations import sar_service
from api.middleware.security import verify_api_security

router = APIRouter(prefix="/api/sar", tags=["SAR"], dependencies=[Depends(verify_api_security)])


@router.get("/{case_id}", response_model=ApiResponse[Dict[str, Any]])
def get_sar_by_case(case_id: str):
    """Retrieves validated FinCEN Suspicious Activity Report record."""
    sar = sar_service.get_sar(case_id)
    return ApiResponse(success=True, data=sar, error=None)
