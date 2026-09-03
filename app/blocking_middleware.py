"""
blocking_middleware.py

The enforcement middleware: sits between incoming requests and route handlers,
runs all four checks in sequence (rate limit volume, rate limit flow, BFLA,
BOLA), and blocks with appropriate HTTP status codes if anything fails.

Every block triggers an alert that goes to the dashboard.
"""

from __future__ import annotations
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import re

from .rate_limiter import RequestRateLimiter, BusinessFlowLimiter
from .authorization import AuthorizationEnforcer, Role


class EnforcementMiddleware(BaseHTTPMiddleware):
    """
    HTTP middleware that enforces rate limits and authorization on every request.
    """

    def __init__(self, app,
                 rate_limiter: RequestRateLimiter | None = None,
                 flow_limiter: BusinessFlowLimiter | None = None,
                 authorizer: AuthorizationEnforcer | None = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RequestRateLimiter()
        self.flow_limiter = flow_limiter or BusinessFlowLimiter()
        self.authorizer = authorizer or AuthorizationEnforcer()

    async def dispatch(self, request: Request, call_next):
        # logic comes in the next commit
        pass