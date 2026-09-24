"""Global search endpoint across cases, entities, and transactions."""

from fastapi import APIRouter, Depends, Query
from typing import Any, Dict, List

from api.schemas.response_schemas import ApiResponse
from api.routes.investigations import investigation_service
from api.middleware.security import verify_api_security

router = APIRouter(prefix="/api/search", tags=["Search"], dependencies=[Depends(verify_api_security)])


@router.get("", response_model=ApiResponse[Dict[str, Any]])
def global_search(q: str = Query(..., min_length=1, description="Search term")):
    """Global search across cases, customer IDs, card IDs, and transaction IDs."""
    term = q.strip().lower()
    repo = investigation_service.repository
    all_cases, _ = repo.list_cases(page_size=1000)

    matched_cases: List[Dict[str, Any]] = []
    matched_customers: List[Dict[str, Any]] = []
    matched_cards: List[Dict[str, Any]] = []
    matched_transactions: List[Dict[str, Any]] = []

    seen_custs = set()
    seen_cards = set()
    seen_txns = set()

    for c in all_cases:
        # Case match
        if (
            term in c.case_id.lower()
            or term in (c.fraud_pattern or "").lower()
            or term in (c.trigger_text or "").lower()
            or term in (c.verdict or "").lower()
        ):
            matched_cases.append({
                "case_id": c.case_id,
                "verdict": c.verdict,
                "pattern": c.fraud_pattern,
                "status": c.status.value,
                "exposure_usd": c.exposure_usd,
            })

        # Customer match
        if c.customer_id and term in c.customer_id.lower() and c.customer_id not in seen_custs:
            seen_custs.add(c.customer_id)
            matched_customers.append({
                "customer_id": c.customer_id,
                "related_case": c.case_id,
                "verdict": c.verdict,
            })

        # Card match
        if c.card_id and term in c.card_id.lower() and c.card_id not in seen_cards:
            seen_cards.add(c.card_id)
            matched_cards.append({
                "card_id": c.card_id,
                "related_case": c.case_id,
                "customer_id": c.customer_id,
            })

        # Transaction match
        if c.flagged_txn_id and term in c.flagged_txn_id.lower() and c.flagged_txn_id not in seen_txns:
            seen_txns.add(c.flagged_txn_id)
            matched_transactions.append({
                "transaction_id": c.flagged_txn_id,
                "related_case": c.case_id,
                "card_id": c.card_id,
                "is_flagged": True,
            })
        for at in c.affected_txn_ids:
            if term in at.lower() and at not in seen_txns:
                seen_txns.add(at)
                matched_transactions.append({
                    "transaction_id": at,
                    "related_case": c.case_id,
                    "card_id": c.card_id,
                    "is_flagged": False,
                })

    return ApiResponse(
        success=True,
        data={
            "query": q,
            "cases": matched_cases[:10],
            "customers": matched_customers[:10],
            "cards": matched_cards[:10],
            "transactions": matched_transactions[:10],
            "total_matches": len(matched_cases) + len(matched_customers) + len(matched_cards) + len(matched_transactions),
        },
        error=None,
    )
