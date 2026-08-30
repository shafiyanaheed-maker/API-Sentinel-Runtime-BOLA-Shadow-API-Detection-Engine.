from app.rate_limiter import RequestRateLimiter


def test_allows_requests_under_the_limit():
    rl = RequestRateLimiter(max_requests=3, window_seconds=5)
    assert rl.check("user_a", "/products").allowed
    assert rl.check("user_a", "/products").allowed
    assert rl.check("user_a", "/products").allowed


def test_blocks_requests_over_the_limit():
    rl = RequestRateLimiter(max_requests=3, window_seconds=5)
    rl.check("user_a", "/products")
    rl.check("user_a", "/products")
    rl.check("user_a", "/products")

    decision = rl.check("user_a", "/products")
    assert decision.allowed is False


def test_different_users_have_separate_limits():
    rl = RequestRateLimiter(max_requests=1, window_seconds=5)
    assert rl.check("user_a", "/products").allowed
    assert rl.check("user_b", "/products").allowed  # different user, own bucket