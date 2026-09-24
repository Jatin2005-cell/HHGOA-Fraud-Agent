"""API Route definitions."""

from .investigations import router as investigations_router
from .cases import router as cases_router
from .evidence import router as evidence_router
from .actions import router as actions_router
from .approvals import router as approvals_router
from .sar import router as sar_router
from .dashboard import router as dashboard_router
from .benchmark import router as benchmark_router
from .audit import router as audit_router
from .search import router as search_router

__all__ = [
    "investigations_router",
    "cases_router",
    "evidence_router",
    "actions_router",
    "approvals_router",
    "sar_router",
    "dashboard_router",
    "benchmark_router",
    "audit_router",
    "search_router",
]

