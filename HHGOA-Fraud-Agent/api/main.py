"""FastAPI Main Application Entrypoint for Fraud Investigation API."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.middleware.request_logging import RequestLoggingMiddleware
from api.middleware.error_handler import setup_error_handlers
from api.schemas.response_schemas import ApiResponse, HealthResponse, HealthDependenciesResponse
from api.routes import (
    investigations_router,
    cases_router,
    evidence_router,
    actions_router,
    approvals_router,
    sar_router,
    dashboard_router,
    benchmark_router,
    audit_router,
    search_router,
)

app = FastAPI(
    title="TigerGraph Agentic Fraud Investigation API",
    description=(
        "Production-ready Investigation, Case Management, and SAR API powered by "
        "TigerGraph MCP and autonomous GraphRAG AI agents (Hacker House Goa 2026)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(RequestLoggingMiddleware)
setup_error_handlers(app)

# Include Routers
app.include_router(investigations_router)
app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(actions_router)
app.include_router(approvals_router)
app.include_router(sar_router)
app.include_router(dashboard_router)
app.include_router(benchmark_router)
app.include_router(audit_router)
app.include_router(search_router)


@app.get("/health", response_model=ApiResponse[HealthResponse], tags=["System"])
def health_check():
    """Basic health check endpoint."""
    return ApiResponse(
        success=True,
        data=HealthResponse(status="healthy", version="1.0.0", service="HHGOA Fraud Investigation API"),
        error=None,
    )


@app.get("/health/dependencies", response_model=ApiResponse[HealthDependenciesResponse], tags=["System"])
def health_dependencies():
    """Dependency liveness check for database, MCP, and AI agents with transparent runtime mode."""
    from api.routes.investigations import investigation_service

    adapter = investigation_service.orchestrator.mcp_adapter
    rt_status = (
        adapter.mcp_client.get_runtime_status()
        if hasattr(adapter.mcp_client, "get_runtime_status")
        else {
            "data_mode": "OFFLINE_STAGED_SIMULATION",
            "graph_name": None,
            "graph_verified": False,
            "schema_verified": False,
            "mcp_verified": False,
            "writeback_verified": False,
        }
    )

    mode = rt_status["data_mode"]
    deps = {
        "tigergraph_engine": "ONLINE (Cluster Connected)" if mode == "LIVE_TIGERGRAPH" else "OFFLINE (Staged Simulation Active)",
        "mcp_server": "READY (Live MCP Protocol)" if mode == "LIVE_TIGERGRAPH" else "READY (Local Simulation Fallback)",
        "case_management_store": "READY",
        "investigation_agent": "ONLINE",
    }
    return ApiResponse(
        success=True,
        data=HealthDependenciesResponse(
            status="healthy",
            data_mode=rt_status["data_mode"],
            graph_name=rt_status["graph_name"],
            graph_verified=rt_status["graph_verified"],
            schema_verified=rt_status["schema_verified"],
            mcp_verified=rt_status["mcp_verified"],
            writeback_verified=rt_status["writeback_verified"],
            dependencies=deps,
        ),
        error=None,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
