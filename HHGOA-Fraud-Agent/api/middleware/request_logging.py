"""Request logging and Correlation ID middleware."""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("APIAccess")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        start_time = time.time()
        response: Response = await call_next(request)
        latency = (time.time() - start_time) * 1000

        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time"] = f"{latency:.2f}ms"

        # Log without sensitive credentials
        logger.info(f"[{req_id}] {request.method} {request.url.path} - {response.status_code} ({latency:.2f}ms)")
        return response
