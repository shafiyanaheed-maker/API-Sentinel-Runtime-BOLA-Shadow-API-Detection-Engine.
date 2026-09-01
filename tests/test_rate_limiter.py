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
    
from app.rate_limiter import BusinessFlowLimiter


def test_flow_limiter_allows_a_few_distinct_objects():
    fl = BusinessFlowLimiter(max_distinct_objects=3, window_seconds=120)
    assert fl.check("user_a", "/api/orders/{id}", "1001").allowed
    assert fl.check("user_a", "/api/orders/{id}", "1002").allowed
    assert fl.check("user_a", "/api/orders/{id}", "1003").allowed


def test_flow_limiter_blocks_object_scan():
    fl = BusinessFlowLimiter(max_distinct_objects=3, window_seconds=120)
    fl.check("user_a", "/api/orders/{id}", "1001")
    fl.check("user_a", "/api/orders/{id}", "1002")
    fl.check("user_a", "/api/orders/{id}", "1003")

    decision = fl.check("user_a", "/api/orders/{id}", "1004")
    assert decision.allowed is False


def test_flow_limiter_does_not_double_count_repeated_object():
    fl = BusinessFlowLimiter(max_distinct_objects=2, window_seconds=120)
    fl.check("user_a", "/api/orders/{id}", "1001")
    # requesting the SAME object again should NOT use up more of the limit
    decision = fl.check("user_a", "/api/orders/{id}", "1001")
    assert decision.allowed is True