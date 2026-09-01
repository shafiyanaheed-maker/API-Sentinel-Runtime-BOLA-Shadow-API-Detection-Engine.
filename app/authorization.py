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


class AuthorizationEnforcer:
    def __init__(self, ownership_map: dict[str, str] | None = None):
        self.ownership_map = ownership_map or MOCK_ORDER_OWNERSHIP

    def check_object_level(self, user_id: str, object_id: str) -> AuthDecision:
        # logic comes in the next commit
        pass