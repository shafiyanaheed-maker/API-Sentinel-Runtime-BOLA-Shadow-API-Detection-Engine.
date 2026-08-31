"""
rate_limiter.py

Provides request-level and business-flow rate limiting for API-Sentinel.

RequestRateLimiter uses a sliding window to limit repeated requests.
BusinessFlowLimiter detects object-scanning behaviour by tracking
distinct object IDs accessed by the same user on the same endpoint pattern.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class RateLimitDecision:
    allowed: bool
    reason: str
    remaining: int


class RequestRateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: int = 10):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._log: dict[str, deque] = defaultdict(deque)

    def check(self, user_id: str, endpoint: str) -> RateLimitDecision:
        """
        Decide whether this request should be allowed.

        Looks up this user+endpoint's recent request history, drops any
        timestamps older than window_seconds, then checks whether the
        remaining count has hit max_requests.
        """
        now = time.time()
        key = f"{user_id}:{endpoint}"
        window = self._log[key]

        while window and now - window[0] > self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            return RateLimitDecision(
                allowed=False,
                reason=(
                    f"Rate limit exceeded: {len(window)}/{self.max_requests} "
                    f"requests in {self.window_seconds}s"
                ),
                remaining=0,
            )

        window.append(now)

        return RateLimitDecision(
            allowed=True,
            reason="within limit",
            remaining=self.max_requests - len(window),
        )


class BusinessFlowLimiter:
    """
    Flags object-scanning behaviour: too many DISTINCT object IDs touched
    by the same user on the same endpoint pattern within a time window.

    This helps detect BOLA-style object enumeration that may avoid the
    normal request-volume limiter.
    """

    def __init__(
        self,
        max_distinct_objects: int = 5,
        window_seconds: int = 30,
    ):
        self.max_distinct_objects = max_distinct_objects
        self.window_seconds = window_seconds
        self._log: dict[str, deque] = defaultdict(deque)

    def check(
        self,
        user_id: str,
        endpoint_pattern: str,
        object_id: str,
    ) -> RateLimitDecision:
        """
        Decide whether the user's object access pattern should be allowed.
        """
        now = time.time()
        key = f"{user_id}:{endpoint_pattern}"
        window = self._log[key]

        while window and now - window[0][0] > self.window_seconds:
            window.popleft()

        distinct_ids = {oid for _, oid in window}
        distinct_ids.add(object_id)

        if len(distinct_ids) > self.max_distinct_objects:
            return RateLimitDecision(
                allowed=False,
                reason=(
                    f"Object-scan pattern detected: "
                    f"{len(distinct_ids)} distinct objects on "
                    f"{endpoint_pattern} in {self.window_seconds}s "
                    f"(limit {self.max_distinct_objects})"
                ),
                remaining=0,
            )

        window.append((now, object_id))

        return RateLimitDecision(
            allowed=True,
            reason="within business-flow limit",
            remaining=self.max_distinct_objects - len(distinct_ids),
        )
