"""
blocking_middleware.py

The enforcement middleware sits between incoming requests and route handlers.

Checks are performed in this order:
1. Allowlist / blocklist
2. IP rate limit for anonymous traffic
3. Request-volume rate limit
4. Business-flow rate limit
5. BFLA authorization
6. BOLA authorization

Blocked requests are recorded in the audit log and generate alerts.
Allowed requests are also recorded in the audit log.
"""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .access_control import access_control
from .alerts import alert_manager
from .audit import audit_logger
from .authorization import AuthorizationEnforcer, Role
from .rate_limiter import (
    BusinessFlowLimiter,
    IPRateLimiter,
    RequestRateLimiter,
)


class EnforcementMiddleware(BaseHTTPMiddleware):
    """
    HTTP middleware that enforces API-Sentinel security controls.
    """

    def __init__(
        self,
        app,
        rate_limiter: RequestRateLimiter | None = None,
        flow_limiter: BusinessFlowLimiter | None = None,
        authorizer: AuthorizationEnforcer | None = None,
        ip_limiter: IPRateLimiter | None = None,
    ):
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

        client_ip = request.client.host if request.client else "unknown"

        # ---------------------------------------------------------
        # 0. ACCESS CONTROL
        # ---------------------------------------------------------
        access_decision = access_control.check(user_id, client_ip)

        if (
            access_decision.matched
            and access_decision.listed_as == "blocked"
        ):
            audit_logger.append(
                user_id=user_id,
                endpoint=endpoint_pattern,
                method=request.method,
                allowed=False,
                reason=access_decision.reason,
            )

            alert_manager.raise_alert(
                violation_type="BLOCKLIST",
                user_id=user_id,
                context=endpoint_pattern,
                reason=access_decision.reason,
            )

            return JSONResponse(
                status_code=403,
                content={
                    "blocked": True,
                    "reason": access_decision.reason,
                },
            )

        if (
            access_decision.matched
            and access_decision.listed_as == "allowed"
        ):
            audit_logger.append(
                user_id=user_id,
                endpoint=endpoint_pattern,
                method=request.method,
                allowed=True,
                reason=access_decision.reason,
            )

            return await call_next(request)

        # ---------------------------------------------------------
        # 1. IP RATE LIMIT
        # Only applies to anonymous / unauthenticated traffic.
        # ---------------------------------------------------------
        if user_id == "anonymous":
            ip_decision = self.ip_limiter.check(
                client_ip,
                endpoint_pattern,
            )

            if not ip_decision.allowed:
                audit_logger.append(
                    user_id=user_id,
                    endpoint=endpoint_pattern,
                    method=request.method,
                    allowed=False,
                    reason=ip_decision.reason,
                )

                alert_manager.raise_alert(
                    violation_type="RATE_LIMIT",
                    user_id=f"ip:{client_ip}",
                    context=endpoint_pattern,
                    reason=ip_decision.reason,
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "blocked": True,
                        "reason": ip_decision.reason,
                    },
                )

        # ---------------------------------------------------------
        # 2. REQUEST VOLUME RATE LIMIT
        # ---------------------------------------------------------
        rl_decision = self.rate_limiter.check(
            user_id,
            endpoint_pattern,
        )

        if not rl_decision.allowed:
            audit_logger.append(
                user_id=user_id,
                endpoint=endpoint_pattern,
                method=request.method,
                allowed=False,
                reason=rl_decision.reason,
            )

            alert_manager.raise_alert(
                violation_type="RATE_LIMIT",
                user_id=user_id,
                context=f"endpoint={endpoint_pattern}",
                reason=rl_decision.reason,
            )

            return JSONResponse(
                status_code=429,
                content={
                    "blocked": True,
                    "reason": rl_decision.reason,
                },
            )

        # ---------------------------------------------------------
        # 3. BUSINESS-FLOW RATE LIMIT
        # Only applies when an object ID exists.
        # ---------------------------------------------------------
        if object_id is not None:
            flow_decision = self.flow_limiter.check(
                user_id,
                endpoint_pattern,
                object_id,
            )

            if not flow_decision.allowed:
                audit_logger.append(
                    user_id=user_id,
                    endpoint=endpoint_pattern,
                    method=request.method,
                    allowed=False,
                    reason=flow_decision.reason,
                )

                alert_manager.raise_alert(
                    violation_type="RATE_LIMIT",
                    user_id=user_id,
                    context=(
                        f"{endpoint_pattern} object_id={object_id}"
                    ),
                    reason=flow_decision.reason,
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "blocked": True,
                        "reason": flow_decision.reason,
                    },
                )

        # ---------------------------------------------------------
        # 4. FUNCTION-LEVEL AUTHORIZATION (BFLA)
        # ---------------------------------------------------------
        func_decision = self.authorizer.check_function_level(
            role,
            endpoint_pattern,
        )

        if not func_decision.allowed:
            audit_logger.append(
                user_id=user_id,
                endpoint=endpoint_pattern,
                method=request.method,
                allowed=False,
                reason=func_decision.reason,
            )

            alert_manager.raise_alert(
                violation_type="BFLA",
                user_id=user_id,
                context=endpoint_pattern,
                reason=func_decision.reason,
            )

            return JSONResponse(
                status_code=403,
                content={
                    "blocked": True,
                    "reason": func_decision.reason,
                },
            )

        # ---------------------------------------------------------
        # 5. OBJECT-LEVEL AUTHORIZATION (BOLA)
        # ---------------------------------------------------------
        if object_id is not None:
            obj_decision = self.authorizer.check_object_level(
                user_id,
                object_id,
            )

            if not obj_decision.allowed:
                audit_logger.append(
                    user_id=user_id,
                    endpoint=endpoint_pattern,
                    method=request.method,
                    allowed=False,
                    reason=obj_decision.reason,
                )

                alert_manager.raise_alert(
                    violation_type="BOLA",
                    user_id=user_id,
                    context=(
                        f"{endpoint_pattern} object_id={object_id}"
                    ),
                    reason=obj_decision.reason,
                )

                return JSONResponse(
                    status_code=403,
                    content={
                        "blocked": True,
                        "reason": obj_decision.reason,
                    },
                )

        # ---------------------------------------------------------
        # ALL CHECKS PASSED
        # ---------------------------------------------------------
        audit_logger.append(
            user_id=user_id,
            endpoint=endpoint_pattern,
            method=request.method,
            allowed=True,
            reason="allowed",
        )

        return await call_next(request)

    def _match_pattern(
        self,
        path: str,
    ) -> tuple[str, str | None]:
        """
        Maps a concrete path such as:

            /api/orders/1001

        to:

            /api/orders/{id}

        and extracts the object ID.
        """

        orders_match = re.match(
            r"^/api/orders/(?P<id>[^/]+)$",
            path,
        )

        if orders_match:
            return (
                "/api/orders/{id}",
                orders_match.group("id"),
            )

        static_endpoints = {
            "/api/products",
            "/api/admin/users",
            "/api/admin/refund",
            "/api/admin/audit",
            "/api/admin/stats",
            "/health",
        }

        if path in static_endpoints:
            return path, None

        return path, None