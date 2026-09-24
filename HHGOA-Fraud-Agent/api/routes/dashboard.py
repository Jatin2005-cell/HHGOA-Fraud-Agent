"""Dashboard aggregation endpoints using real CaseRepository data.

NULL SEMANTICS (verified 2026-09-20):
  fraud_probability = None  →  UNKNOWN / NOT YET CALCULATED
    These are NEW/unprocessed cases that have a risk_score from the alert system
    but have not been processed by the investigation agent yet.
    fraud_probability is only set after the agent completes analysis.
  risk_score = None  →  Not provided by the alert trigger (manual/analyst cases)

Aggregation rules:
  - High-risk KPI: use risk_score if fp is unknown, exclude from fp average if None
  - Distribution: use best available score (fp preferred, fallback to risk_score)
  - Cases with BOTH None: placed in "Pending Assessment" band, not Low Risk
"""

from fastapi import APIRouter, Depends
from typing import Any, Dict, List
from collections import Counter

from api.schemas.response_schemas import ApiResponse
from api.routes.investigations import investigation_service
from api.middleware.security import verify_api_security

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"], dependencies=[Depends(verify_api_security)])


def _best_risk_score(c) -> float | None:
    """Returns the best available risk score for a case.
    fraud_probability is authoritative (agent-computed).
    risk_score is the pre-screening alert score used when fp is not yet computed.
    Returns None if neither is available (genuinely unknown).
    """
    if c.fraud_probability is not None:
        return c.fraud_probability
    if c.risk_score is not None:
        return c.risk_score
    return None


@router.get("/summary", response_model=ApiResponse[Dict[str, Any]])
def get_dashboard_summary():
    """Computes executive operational KPIs directly from real stored cases.

    NULL semantics: fraud_probability=None means NOT YET ASSESSED.
    High-risk detection uses best_risk_score (fp preferred, fallback to risk_score).
    Cases with both None are counted in total but excluded from risk-band KPI
    to avoid misrepresenting uninvestigated cases as low risk.
    """
    repo = investigation_service.repository
    all_cases, total = repo.list_cases(page_size=1000)

    open_statuses = {"NEW", "INVESTIGATING", "EVIDENCE_PENDING", "REVIEW", "ACTION_REQUIRED", "APPROVAL_PENDING"}
    open_count = sum(1 for c in all_cases if c.status.value in open_statuses)

    # Use best available score; exclude if both are None (case is pending assessment)
    high_risk_count = sum(
        1 for c in all_cases
        if _best_risk_score(c) is not None and _best_risk_score(c) >= 0.7
    )
    pending_assessment_count = sum(
        1 for c in all_cases
        if _best_risk_score(c) is None
    )

    pending_approvals = sum(
        1 for c in all_cases
        if c.approval_status == "PENDING" or c.status.value == "APPROVAL_PENDING"
    )
    sar_required_count = sum(1 for c in all_cases if c.sar_required)
    fraud_count = sum(1 for c in all_cases if c.verdict == "fraud" or c.verdict == "CONFIRMED_FRAUD")
    uncertain_count = sum(1 for c in all_cases if c.verdict == "uncertain" or c.verdict == "SUSPICIOUS")
    legitimate_count = sum(1 for c in all_cases if c.verdict == "legitimate" or c.verdict == "LEGITIMATE")
    total_exposure = sum(c.exposure_usd for c in all_cases)

    return ApiResponse(
        success=True,
        data={
            "total_cases": total,
            "open_investigations": open_count,
            "high_risk_cases": high_risk_count,
            "pending_assessment": pending_assessment_count,
            "pending_approvals": pending_approvals,
            "sar_required": sar_required_count,
            "fraud_investigations": fraud_count,
            "uncertain_cases": uncertain_count,
            "legitimate_cases": legitimate_count,
            "total_exposure_usd": round(total_exposure, 2),
        },
        error=None,
    )


@router.get("/distribution", response_model=ApiResponse[Dict[str, Any]])
def get_dashboard_distributions():
    """Returns distribution breakdowns for status, fraud pattern, risk bands, and approvals.

    NULL semantics: Cases where both fraud_probability and risk_score are None
    are placed in a distinct 'Pending Assessment' band rather than 'Low (<0.4)'
    to avoid distorting risk analytics with uninvestigated cases.
    """
    repo = investigation_service.repository
    all_cases, _ = repo.list_cases(page_size=1000)

    status_counts = Counter(c.status.value for c in all_cases)
    pattern_counts = Counter(c.fraud_pattern for c in all_cases if c.fraud_pattern)
    approval_counts = Counter(c.approval_route for c in all_cases if c.approval_route)

    # Risk tiers — use best_risk_score; None → "Pending Assessment"
    risk_bands = {"High (>=0.7)": 0, "Medium (0.4-0.69)": 0, "Low (<0.4)": 0, "Pending Assessment": 0}
    for c in all_cases:
        score = _best_risk_score(c)
        if score is None:
            risk_bands["Pending Assessment"] += 1
        elif score >= 0.7:
            risk_bands["High (>=0.7)"] += 1
        elif score >= 0.4:
            risk_bands["Medium (0.4-0.69)"] += 1
        else:
            risk_bands["Low (<0.4)"] += 1

    by_status = [{"name": k, "count": v} for k, v in status_counts.items()]
    by_pattern = [{"name": k.replace("_", " ").title(), "count": v} for k, v in pattern_counts.items()]
    by_risk = [{"band": k, "count": v} for k, v in risk_bands.items()]
    by_approval = [{"route": k.upper(), "count": v} for k, v in approval_counts.items()]

    return ApiResponse(
        success=True,
        data={
            "cases_by_status": by_status,
            "cases_by_pattern": by_pattern,
            "risk_distribution": by_risk,
            "approval_distribution": by_approval,
        },
        error=None,
    )


@router.get("/activity", response_model=ApiResponse[List[Dict[str, Any]]])
def get_recent_activity(limit: int = 10):
    """Returns recent cases for quick executive activity tracking."""
    repo = investigation_service.repository
    all_cases, _ = repo.list_cases(page_size=limit)
    items = [
        {
            "case_id": c.case_id,
            "trigger_type": c.trigger_type,
            "verdict": c.verdict,
            "pattern": c.fraud_pattern,
            "exposure_usd": c.exposure_usd,
            "status": c.status.value,
            "approval_route": c.approval_route,
            "updated_at": c.updated_at,
        }
        for c in all_cases[:limit]
    ]
    return ApiResponse(success=True, data=items, error=None)
