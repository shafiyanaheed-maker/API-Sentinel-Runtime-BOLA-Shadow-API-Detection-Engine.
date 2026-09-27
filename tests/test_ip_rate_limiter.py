"""
tests/test_ip_rate_limiter.py

Unit tests for IPRateLimiter (app/rate_limiter.py). Tests the limiter in
isolation, without going through the HTTP middleware.
"""

import pytest

from app.rate_limiter import IPRateLimiter


@pytest.fixture
def ip_limiter() -> IPRateLimiter:
    """Fresh IPRateLimiter with a small window for fast, deterministic tests."""
    return IPRateLimiter(max_requests=5, window_seconds=10)


def test_allows_requests_under_the_limit(ip_limiter: IPRateLimiter):
    for _ in range(5):
        decision = ip_limiter.check("1.2.3.4", "/api/products")
        assert decision.allowed is True


def test_blocks_requests_over_the_limit(ip_limiter: IPRateLimiter):
    for _ in range(5):
        ip_limiter.check("1.2.3.4", "/api/products")

    decision = ip_limiter.check("1.2.3.4", "/api/products")

    assert decision.allowed is False
    assert "IP rate limit exceeded" in decision.reason
    assert decision.remaining == 0


def test_remaining_count_decreases_correctly(ip_limiter: IPRateLimiter):
    first = ip_limiter.check("1.2.3.4", "/api/products")
    second = ip_limiter.check("1.2.3.4", "/api/products")

    assert first.remaining == 4
    assert second.remaining == 3


def test_different_ips_are_tracked_independently(ip_limiter: IPRateLimiter):
    for _ in range(5):
        ip_limiter.check("1.2.3.4", "/api/products")

    # A different IP should not be affected by the first IP's usage
    decision = ip_limiter.check("5.6.7.8", "/api/products")

    assert decision.allowed is True


def test_different_endpoints_are_tracked_independently(ip_limiter: IPRateLimiter):
    for _ in range(5):
        ip_limiter.check("1.2.3.4", "/api/products")

    # Same IP, different endpoint should not be affected
    decision = ip_limiter.check("1.2.3.4", "/api/orders/{id}")

    assert decision.allowed is True


def test_window_resets_after_expiry(ip_limiter: IPRateLimiter, monkeypatch):
    import time as time_module

    current_time = [1000.0]
    monkeypatch.setattr(time_module, "time", lambda: current_time[0])

    for _ in range(5):
        ip_limiter.check("1.2.3.4", "/api/products")

    # Should be blocked now
    assert ip_limiter.check("1.2.3.4", "/api/products").allowed is False

    # Advance time past the window
    current_time[0] += 11

    # Should be allowed again since the old timestamps expired
    decision = ip_limiter.check("1.2.3.4", "/api/products")
    assert decision.allowed is True
