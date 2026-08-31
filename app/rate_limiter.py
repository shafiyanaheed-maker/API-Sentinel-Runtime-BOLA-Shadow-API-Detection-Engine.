"""
rate_limiter.py

Limits how often a user can hit an API endpoint, to stop bots and
abuse. Uses a "sliding window": we track WHEN each request happened,
and only count the ones from the last few seconds.
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
        timestamps older than `window_seconds`, then checks whether the
        remaining count has hit `max_requests`. If so, blocks the request.
        Otherwise records this request and allows it.
        """
        now = time.time()
        key = f"{user_id}:{endpoint}"
        window = self._log[key]

        # Step 1: remove timestamps older than our window
        while window and now - window[0] > self.window_seconds:
            window.popleft()

        # Step 2: check if we're already at the limit
        if len(window) >= self.max_requests:
            return RateLimitDecision(
                allowed=False,
                reason=f"Rate limit exceeded: {len(window)}/{self.max_requests} requests in {self.window_seconds}s",
                remaining=0,
            )

        # Step 3: record this request and allow it
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
    Catches a BOLA attacker who scans slowly enough to dodge the volume
    limiter above.
    """

    def __init__(self, max_distinct_objects: int = 5, window_seconds: int = 30):
        self.max_distinct_objects = max_distinct_objects
        self.window_seconds = window_seconds
        self._log: dict[str, deque] = defaultdict(deque)

    def check(self, user_id: str, endpoint_pattern: str, object_id: str) -> RateLimitDecision:
        # logic comes in the next commit
        pass