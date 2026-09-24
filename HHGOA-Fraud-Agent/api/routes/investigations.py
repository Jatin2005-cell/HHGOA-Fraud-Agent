"""Investigation API Routes."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List

from api.schemas.request_schemas import InvestigationCreateRequest, EvidenceRequestPayload
from api.schemas.response_schemas import ApiResponse
from api.services.investigation_service import InvestigationService
from api.services.evidence_service import EvidenceService
from api.services.action_service import ActionService
from api.services.approval_service import ApprovalService
from api.services.sar_service import SARService
from api.middleware.security import verify_api_security, sanitize_input_string

router = APIRouter(prefix="/api/investigations", tags=["Investigations"], dependencies=[Depends(verify_api_security)])

# Shared service instances
investigation_service = InvestigationService()
evidence_service = EvidenceService(investigation_service.repository)
action_service = ActionService(investigation_service.repository)
approval_service = ApprovalService(investigation_service.repository)
sar_service = SARService(investigation_service.repository)


@router.post("", response_model=ApiResponse[Dict[str, Any]], status_code=201)
def create_investigation(payload: InvestigationCreateRequest):
    """Creates a new investigation case from alert trigger."""
    sanitize_input_string(payload.case_id)
    sanitize_input_string(payload.trigger_text)
    record = investigation_service.create_investigation(payload.model_dump())
    return ApiResponse(success=True, data=record.model_dump(), error=None)


@router.post("/{case_id}/run", response_model=ApiResponse[Dict[str, Any]])
def run_investigation(case_id: str):
    """Runs Phase 5 AI agent over the case, performs graph writeback & readback verification."""
    result = investigation_service.run_investigation(case_id)
    return ApiResponse(success=True, data=result, error=None)


@router.get("/{case_id}", response_model=ApiResponse[Dict[str, Any]])
def get_investigation(case_id: str):
    """Retrieves full investigation case record."""
    case = investigation_service.repository.get_case(case_id)
    if not case:
        raise KeyError(f"Case {case_id} not found.")
    return ApiResponse(success=True, data=case.model_dump(), error=None)


@router.get("/{case_id}/timeline", response_model=ApiResponse[List[Dict[str, Any]]])
def get_timeline(case_id: str):
    """Retrieves chronological investigation timeline events."""
    events = investigation_service.get_timeline(case_id)
    return ApiResponse(success=True, data=[e.model_dump() for e in events], error=None)


@router.get("/{case_id}/evidence", response_model=ApiResponse[Dict[str, Any]])
def get_evidence(case_id: str):
    """Retrieves provenanced evidence items for case."""
    ev = evidence_service.get_evidence(case_id)
    return ApiResponse(success=True, data=ev, error=None)


@router.get("/{case_id}/actions", response_model=ApiResponse[Dict[str, Any]])
def get_actions(case_id: str):
    """Retrieves initial and final recommended actions and what changed."""
    acts = action_service.get_actions(case_id)
    return ApiResponse(success=True, data=acts, error=None)


@router.get("/{case_id}/approval", response_model=ApiResponse[Dict[str, Any]])
def get_approval(case_id: str):
    """Retrieves current approval route and status."""
    appr = approval_service.get_approval_status(case_id)
    return ApiResponse(success=True, data=appr, error=None)


@router.get("/{case_id}/sar", response_model=ApiResponse[Dict[str, Any]])
def get_sar(case_id: str):
    """Retrieves FinCEN SAR record if mandated by policy."""
    sar = sar_service.get_sar(case_id)
    return ApiResponse(success=True, data=sar, error=None)


@router.post("/{case_id}/evidence-request", response_model=ApiResponse[Dict[str, Any]])
def create_evidence_request(case_id: str, payload: EvidenceRequestPayload):
    """Issues a controlled additional evidence inquiry (customer validation / step-up auth)."""
    case = investigation_service.repository.get_case(case_id)
    if not case:
        raise KeyError(f"Case {case_id} not found.")

    new_req = {
        "type": payload.request_type,
        "question": sanitize_input_string(payload.question),
        "assumed_response": f"SIMULATED TEST EVIDENCE: {sanitize_input_string(payload.assumed_response)}",
        "step": len(case.evidence),
    }
    case.evidence_requests.append(new_req)
    investigation_service.repository.update_case(case_id, {"evidence_requests": case.evidence_requests})

    return ApiResponse(
        success=True,
        data={"case_id": case_id, "evidence_request": new_req},
        error=None,
    )


@router.get("/{case_id}/graph", response_model=ApiResponse[Dict[str, Any]])
def get_investigation_graph(case_id: str):
    """Retrieves verified graph topology (nodes and edges) for a case."""
    case = investigation_service.repository.get_case(case_id)
    if not case:
        raise KeyError(f"Case {case_id} not found.")

    nodes = []
    edges = []

    # Case Node
    nodes.append({
        "id": case.case_id,
        "type": "DynamicCase",
        "label": f"Case {case.case_id}",
        "metadata": {
            "verdict": case.verdict,
            "pattern": case.fraud_pattern,
            "status": case.status.value if hasattr(case.status, "value") else str(case.status),
            "exposure_usd": case.exposure_usd,
            "fraud_probability": case.fraud_probability,
        },
    })

    # Customer Node
    if case.customer_id:
        nodes.append({
            "id": case.customer_id,
            "type": "Customer",
            "label": f"Customer {case.customer_id}",
            "metadata": {"role": "Primary Account Holder"},
        })
        edges.append({
            "source": case.case_id,
            "target": case.customer_id,
            "relationship": "INVESTIGATES_CUSTOMER",
        })

    # Card Node
    if case.card_id:
        nodes.append({
            "id": case.card_id,
            "type": "Card",
            "label": f"Card {case.card_id}",
            "metadata": {"status": "FLAGGED"},
        })
        edges.append({
            "source": case.case_id,
            "target": case.card_id,
            "relationship": "CASE_ON_CARD",
        })
        if case.customer_id:
            edges.append({
                "source": case.customer_id,
                "target": case.card_id,
                "relationship": "OWNS_CARD",
            })

    # Connected Cards
    for cc in case.connected_card_ids:
        if cc != case.card_id:
            nodes.append({
                "id": cc,
                "type": "Card",
                "label": f"Connected Card {cc}",
                "metadata": {"status": "ASSOCIATED"},
            })
            if case.card_id:
                edges.append({
                    "source": case.card_id,
                    "target": cc,
                    "relationship": "CONNECTED_CARD",
                })

    # Transactions (flagged & affected)
    txns = list(dict.fromkeys(([case.flagged_txn_id] if case.flagged_txn_id else []) + case.affected_txn_ids))
    for t in txns:
        is_flagged = t == case.flagged_txn_id
        nodes.append({
            "id": t,
            "type": "Transaction",
            "label": f"Txn {t}",
            "metadata": {
                "is_flagged": is_flagged,
                "status": "FLAGGED_ORIGIN" if is_flagged else "SUSPICIOUS_CLUSTER",
            },
        })
        edges.append({
            "source": case.case_id,
            "target": t,
            "relationship": "CASE_INVOLVES",
        })
        if case.card_id:
            edges.append({
                "source": case.card_id,
                "target": t,
                "relationship": "TRANSACTION_ON_CARD",
            })

    # Devices
    for dev in case.connected_device_profiles:
        nodes.append({
            "id": dev,
            "type": "DeviceProfile",
            "label": f"Device {dev}",
            "metadata": {"profile": dev},
        })
        if case.card_id:
            edges.append({
                "source": case.card_id,
                "target": dev,
                "relationship": "USED_DEVICE",
            })

    # Similar Historical Precedents
    for pc in case.similar_prior_cases:
        nodes.append({
            "id": pc,
            "type": "ClosedCase",
            "label": f"Historical {pc}",
            "metadata": {"precedent": True},
        })
        edges.append({
            "source": case.case_id,
            "target": pc,
            "relationship": "SIMILAR_PRECEDENT",
        })

    return ApiResponse(
        success=True,
        data={"case_id": case_id, "nodes": nodes, "edges": edges},
        error=None,
    )

