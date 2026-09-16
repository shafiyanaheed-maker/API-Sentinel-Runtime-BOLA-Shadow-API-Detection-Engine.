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
        user_id = request.headers.get("X-User-Id", "anonymous")
        role_header = request.headers.get("X-User-Role", "user")
        role = Role.ADMIN if role_header == "admin" else Role.USER
        
        endpoint_pattern, object_id = self._match_pattern(request.url.path)

        # 1. Volume rate limit
        rl_decision = self.rate_limiter.check(user_id, endpoint_pattern)
        if not rl_decision.allowed:
            return JSONResponse(
                status_code=429,
                content={"blocked": True, "reason": rl_decision.reason},
            )

        # 2. Business-flow rate limit (only if there's an object_id)
        if object_id is not None:
            flow_decision = self.flow_limiter.check(user_id, endpoint_pattern, object_id)
            if not flow_decision.allowed:
                return JSONResponse(
                    status_code=429,
                    content={"blocked": True, "reason": flow_decision.reason},
                )

        # 3. Function-level authorization (BFLA)
        func_decision = self.authorizer.check_function_level(role, endpoint_pattern)
        if not func_decision.allowed:
            return JSONResponse(
                status_code=403,
                content={"blocked": True, "reason": func_decision.reason},
            )

        # 4. Object-level authorization (BOLA) - only if there's an object_id
        if object_id is not None:
            obj_decision = self.authorizer.check_object_level(user_id, object_id)
            if not obj_decision.allowed:
                return JSONResponse(
                    status_code=403,
                    content={"blocked": True, "reason": obj_decision.reason},
                )

        # All checks passed - let the request through
        return await call_next(request)

    def _match_pattern(self, path: str) -> tuple[str, str | None]:
        """
        Maps a concrete path like /api/orders/1001 to its pattern (/api/orders/{id})
        and extracts the object_id (1001).
        Returns (endpoint_pattern, object_id_or_None).
        """
        # Pattern for /api/orders/{id}
        orders_match = re.match(r"^/api/orders/(?P<id>[^/]+)$", path)
        if orders_match:
            return "/api/orders/{id}", orders_match.group("id")
        
        # Static endpoints with no object_id
        static_endpoints = {"/api/products", "/api/admin/users", "/api/admin/refund", "/health"}
        if path in static_endpoints:
            return path, None
        
        # Unknown endpoint
        return path, None