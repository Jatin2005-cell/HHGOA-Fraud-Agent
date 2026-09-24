"""Global exception handlers for standardized API error responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from case_management.case_lifecycle import LifecycleTransitionError


def setup_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload schema.",
                    "details": exc.errors(),
                },
            },
        )

    @app.exception_handler(LifecycleTransitionError)
    async def lifecycle_exception_handler(request: Request, exc: LifecycleTransitionError):
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INVALID_LIFECYCLE_TRANSITION",
                    "message": str(exc),
                },
            },
        )

    @app.exception_handler(KeyError)
    async def not_found_exception_handler(request: Request, exc: KeyError):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": str(exc).strip("'"),
                },
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "BAD_REQUEST",
                    "message": str(exc),
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Do not expose internal stack traces or database errors
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred processing the request.",
                },
            },
        )
