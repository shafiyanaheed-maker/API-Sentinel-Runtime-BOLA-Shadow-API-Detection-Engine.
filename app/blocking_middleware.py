"""
blocking_middleware.py

The enforcement middleware: sits between incoming requests and route handlers,
runs all checks in sequence (allowlist/blocklist, IP rate limit, volume
rate limit, flow rate limit, BFLA, BOLA), and blocks with appropriate HTTP
status codes if anything fails.

Every block triggers an alert (logged + optionally sent to a webhook) and
is recorded to the audit log. Every request, allowed or blocked, is
recorded to the audit log.
"""

from __future__ import annotations
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import re

from .rate_limiter import RequestRateLimiter, BusinessFlowLimiter, IPRateLimiter
from .authorization import AuthorizationEnforcer, Role
from .audit import audit_logger
from .alerts import alert_manager
from .access_control import access_control


class EnforcementMiddleware(BaseHTTPMiddleware):
    """
    HTTP middleware that enforces rate limits and authorization on every request.
    """

    def __init__(self, app,
                 rate_limiter: RequestRateLimiter | None = None,
                 flow_limiter: BusinessFlowLimiter | None = None,
                 authorizer: AuthorizationEnforcer | None = None,
                 ip_limiter: IPRateLimiter | None = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RequestRateLimiter()
        self.flow_limiter = flow_limiter or BusinessFlowLimiter()
        self.authorizer = authorizer or AuthorizationEnforcer()
        self.ip_limiter = ip_limiter or IPRateLimiter()

    async def dispatch(self, request: Request, call_next):
        user_id = request.headers.get("X-User-Id", "anonymous")
        role_header = request.headers.get("X-User-Role", "user")
        role = Role.ADMIN if role_header == "admin" else Role.USER

        endpoint_pattern, object_id = self._match_pattern(request.url.path)

        # -1. Access control (allowlist/blocklist) - checked before
        # everything else. Blocklisted entities are rejected immediately;
        # allowlisted entities skip every other check.
        client_ip = request.client.host if request.client else "unknown"
        access_decision = access_control.check(user_id, client_ip)

        if access_decision.matched and access_decision.listed_as == "blocked":
            audit_logger.append(
                user_id=user_id, endpoint=endpoint_pattern, method=request.method,
                allowed=False, reason=access_decision.reason,
            )
            alert_manager.raise_alert(
                violation_type="BLOCKLIST",
                user_id=user_id,
                context=endpoint_pattern,
                reason=access_decision.reason,
            )
            return JSONResponse(
                status_code=403,
                content={"blocked": True, "reason": access_decision.reason},
            )

        if access_decision.matched and access_decision.listed_as == "allowed":
            audit_logger.append(
                user_id=user_id, endpoint=endpoint_pattern, method=request.method,
                allowed=True, reason=access_decision.reason,
            )
            return await call_next(request)

        # 0. IP rate limit - only for anonymous/unauthenticated traffic.
        if user_id == "anonymous":
            ip_decision = self.ip_limiter.check(client_ip, endpoint_pattern)
            if not ip_decision.allowed:
                audit_logger.append(
                    user_id=user_id, endpoint=endpoint_pattern, method=request.method,
                    allowed=False, reason=ip_decision.reason,
                )
                alert_manager.raise_alert(
                    violation_type="RATE_LIMIT",
                    user_id=f"ip:{client_ip}",
                    context=endpoint_pattern,
                    reason=ip_decision.reason,
                )
                return JSONResponse(
                    status_code=429,
                    content={"blocked": True, "reason": ip_decision.reason},
                )

        # 1. Volume rate limit
        rl_decision = self.rate_limiter.check(user_id, endpoint_pattern)
        if not rl_decision.allowed:
            audit_logger.append(
                user_id=user_id, endpoint=endpoint_pattern, method=request.method,
                allowed=False, reason=rl_decision.reason,
            )
            alert_manager.raise_alert(
                violation_type="RATE_LIMIT",
                user_id=user_id,
                context=endpoint_pattern,
                reason=rl_decision.reason,
            )
            return JSONResponse(
                status_code=429,
                content={"blocked": True, "reason": rl_decision.reason},
            )

        # 2. Business-flow rate limit (only if there's an object_id)
        if object_id is not None:
            flow_decision = self.flow_limiter.check(user_id, endpoint_pattern, object_id)
            if not flow_decision.allowed:
                audit_logger.append(
                    user_id=user_id, endpoint=endpoint_pattern, method=request.method,
                    allowed=False, reason=flow_decision.reason,
                )
                alert_manager.raise_alert(
                    violation_type="RATE_LIMIT",
                    user_id=user_id,
                    context=f"{endpoint_pattern} object_id={object_id}",
                    reason=flow_decision.reason,
                )
                return JSONResponse(
                    status_code=429,
                    content={"blocked": True, "reason": flow_decision.reason},
                )

        # 3. Function-level authorization (BFLA)
        func_decision = self.authorizer.check_function_level(role, endpoint_pattern)
        if not func_decision.allowed:
            audit_logger.append(
                user_id=user_id, endpoint=endpoint_pattern, method=request.method,
                allowed=False, reason=func_decision.reason,
            )
            alert_manager.raise_alert(
                violation_type="BFLA",
                user_id=user_id,
                context=endpoint_pattern,
                reason=func_decision.reason,
            )
            return JSONResponse(
                status_code=403,
                content={"blocked": True, "reason": func_decision.reason},
            )

        # 4. Object-level authorization (BOLA) - only if there's an object_id
        if object_id is not None:
            obj_decision = self.authorizer.check_object_level(user_id, object_id)
            if not obj_decision.allowed:
                audit_logger.append(
                    user_id=user_id, endpoint=endpoint_pattern, method=request.method,
                    allowed=False, reason=obj_decision.reason,
                )
                alert_manager.raise_alert(
                    violation_type="BOLA",
                    user_id=user_id,
                    context=f"{endpoint_pattern} object_id={object_id}",
                    reason=obj_decision.reason,
                )
                return JSONResponse(
                    status_code=403,
                    content={"blocked": True, "reason": obj_decision.reason},
                )

        # All checks passed - let the request through
        audit_logger.append(
            user_id=user_id, endpoint=endpoint_pattern, method=request.method,
            allowed=True, reason="all checks passed",
        )
        return await call_next(request)

    def _match_pattern(self, path: str) -> tuple[str, str | None]:
        """
        Maps a concrete path like /api/orders/1001 to its pattern (/api/orders/{id})
        and extracts the object_id (1001).
        Returns (endpoint_pattern, object_id_or_None).
        """
        orders_match = re.match(r"^/api/orders/(?P<id>[^/]+)$", path)
        if orders_match:
            return "/api/orders/{id}", orders_match.group("id")

        static_endpoints = {"/api/products", "/api/admin/users", "/api/admin/refund", "/health"}
        if path in static_endpoints:
            return path, None

        return path, None
