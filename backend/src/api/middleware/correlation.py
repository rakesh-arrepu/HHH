from typing import Optional
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from core.exceptions import correlation_id_var


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Sets/propagates a per-request correlation ID.
    - Reads incoming header 'X-Request-Id' if present, otherwise generates a UUID4.
    - Stores it on request.state.correlation_id and in a ContextVar for deeper layers.
    - Adds 'X-Correlation-Id' response header for client-side tracing.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-Id", response_header: str = "X-Correlation-Id"):
        super().__init__(app)
        self.header_name = header_name
        self.response_header = response_header

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        corr_id: str = request.headers.get(self.header_name) or str(uuid4())
        try:
            request.state.correlation_id = corr_id
        except Exception:
            # Non-fatal; continue without request.state if necessary
            pass
        # Populate context var for downstream usage (GraphQL error formatter, logs, etc.)
        correlation_id_var.set(corr_id)

        response = await call_next(request)
        try:
            response.headers[self.response_header] = corr_id
        except Exception:
            # Non-fatal; skip header if unsupported
            pass
        return response
