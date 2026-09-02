"""
authorization.py

Checks whether a user is allowed to access a specific object (BOLA check).
Later this will also check whether a user's ROLE allows them to call a
given endpoint at all (BFLA check) - that comes in a future commit.

In the real system, ownership data comes from Vyshnavi's database. Here
it's a small mock table so this module can be built and tested
independently, without waiting on the backend.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

@dataclass
class AuthDecision:
    allowed: bool
    violation_type: str | None  # "BOLA" or None
    reason: str


# Mock data: object_id -> the user_id who actually owns it
MOCK_ORDER_OWNERSHIP = {
    "1001": "user_a",
    "1002": "user_a",
    "1003": "user_b",
    "1004": "user_b",
    "1005": "user_c",
}

# Mock data: endpoint pattern -> set of roles allowed to call it
MOCK_ENDPOINT_ROLES = {
    "/api/orders/{id}": {Role.USER, Role.ADMIN},
    "/api/admin/users": {Role.ADMIN},
    "/api/admin/refund": {Role.ADMIN},
    "/api/products": {Role.USER, Role.ADMIN},
}

class AuthorizationEnforcer:
    def __init__(self,
                 ownership_map: dict[str, str] | None = None,
                 role_map: dict[str, set[Role]] | None = None):
        self.ownership_map = ownership_map or MOCK_ORDER_OWNERSHIP
        self.role_map = role_map or MOCK_ENDPOINT_ROLES

    def check_object_level(self, user_id: str, object_id: str) -> AuthDecision:
        owner = self.ownership_map.get(object_id)

        if owner is None:
            # The object doesn't exist in our records at all - that's a
            # "not found" situation, not an authorization violation, so
            # we let it through and let a 404 handler deal with it later.
            return AuthDecision(
                allowed=True,
                violation_type=None,
                reason="object not found (not an authorization decision)",
            )

        if owner != user_id:
            return AuthDecision(
                allowed=False,
                violation_type="BOLA",
                reason=f"user '{user_id}' attempted to access object '{object_id}' "
                       f"owned by '{owner}'",
            )

        return AuthDecision(
            allowed=True,
            violation_type=None,
            reason="owner match",
        )
        
    def check_function_level(self, role: Role, endpoint_pattern: str) -> AuthDecision:
        # logic comes in the next commit
        pass