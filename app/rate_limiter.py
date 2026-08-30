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
        # logic comes in the next commit
        pass