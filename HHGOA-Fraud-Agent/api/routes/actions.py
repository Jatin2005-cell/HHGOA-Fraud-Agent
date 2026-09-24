"""Action API Routes."""

from fastapi import APIRouter, Depends
from typing import Any, Dict
from api.schemas.response_schemas import ApiResponse
from api.routes.investigations import action_service
from api.middleware.security import verify_api_security

router = APIRouter(prefix="/api/actions", tags=["Actions"], dependencies=[Depends(verify_api_security)])


@router.get("/{case_id}", response_model=ApiResponse[Dict[str, Any]])
def get_actions_by_case(case_id: str):
    """Retrieves initial and final recommended actions with approval routing."""
    acts = action_service.get_actions(case_id)
    return ApiResponse(success=True, data=acts, error=None)
