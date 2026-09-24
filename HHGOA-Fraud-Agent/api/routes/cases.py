"""Case Management API Routes."""

from fastapi import APIRouter, Depends, Query
from typing import Any, Dict, Optional

from api.schemas.case_schemas import CaseListResponse, CaseResponse
from api.schemas.response_schemas import ApiResponse
from api.services.case_service import CaseService
from api.routes.investigations import investigation_service
from api.middleware.security import verify_api_security

router = APIRouter(prefix="/api/cases", tags=["Cases"], dependencies=[Depends(verify_api_security)])
case_service = CaseService(investigation_service.repository)


@router.get("", response_model=ApiResponse[CaseListResponse])
def list_cases(
    status: Optional[str] = Query(None, description="Case lifecycle status (e.g. INVESTIGATING, RESOLVED)"),
    pattern: Optional[str] = Query(None, description="Fraud pattern name"),
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    card_id: Optional[str] = Query(None, description="Card ID filter"),
    risk_level: Optional[str] = Query(None, description="HIGH | MEDIUM | LOW"),
    approval_status: Optional[str] = Query(None, description="PENDING | APPROVED | REJECTED"),
    sar_status: Optional[str] = Query(None, description="GENERATED | REVIEW_REQUIRED | NOT_REQUIRED"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Retrieves paginated and filtered fraud cases."""
    cases, total = case_service.list_cases(
        status=status,
        pattern=pattern,
        customer_id=customer_id,
        card_id=card_id,
        risk_level=risk_level,
        approval_status=approval_status,
        sar_status=sar_status,
        page=page,
        page_size=page_size,
    )

    items = [
        CaseResponse(
            case_id=c.case_id,
            status=c.status.value,
            created_at=c.created_at,
            updated_at=c.updated_at,
            trigger_type=c.trigger_type,
            trigger_text=c.trigger_text,
            flagged_txn_id=c.flagged_txn_id,
            customer_id=c.customer_id,
            card_id=c.card_id,
            verdict=c.verdict,
            fraud_probability=c.fraud_probability,
            risk_score=c.risk_score,
            fraud_pattern=c.fraud_pattern,
            pattern_description=c.pattern_description,
            affected_txn_ids=c.affected_txn_ids,
            exposure_usd=c.exposure_usd,
            connected_card_ids=c.connected_card_ids,
            connected_device_profiles=c.connected_device_profiles,
            approval_route=c.approval_route,
            approval_status=c.approval_status,
            sar_required=c.sar_required,
            sar_status=c.sar_status,
            summary=c.summary,
            stop_reason=c.stop_reason,
        )
        for c in cases
    ]

    return ApiResponse(
        success=True,
        data=CaseListResponse(items=items, total=total, page=page, page_size=page_size),
        error=None,
    )


@router.get("/{case_id}", response_model=ApiResponse[Dict[str, Any]])
def get_case_by_id(case_id: str):
    """Retrieves single persistent case by ID."""
    case = case_service.get_case(case_id)
    return ApiResponse(success=True, data=case.model_dump(), error=None)
