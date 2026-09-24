"""Standard API Response schemas."""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    service: str = "HHGOA Fraud Investigation Engine API"


class HealthDependenciesResponse(BaseModel):
    status: str
    data_mode: str
    graph_name: Optional[str] = None
    graph_verified: bool = False
    schema_verified: bool = False
    mcp_verified: bool = False
    writeback_verified: bool = False
    dependencies: Dict[str, str]
