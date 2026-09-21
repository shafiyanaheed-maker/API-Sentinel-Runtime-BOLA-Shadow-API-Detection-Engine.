"""
ip_flood_attack.py

Simulates an attacker who dodges the per-user rate limiter by never
setting X-User-Id (or rotating it on every request), relying purely on
IP-based volume to abuse an endpoint. This is exactly the gap
IPRateLimiter closes -- the per-user RequestRateLimiter alone would see
each request as a "fresh" anonymous user and never trigger.

Usage:
    python -m simulation.ip_flood_attack
"""

import requests

HOST = "http://127.0.0.1:8000"


def anonymous_flood(n=35):
    """
    Burst of requests with NO X-User-Id header at all -- pure anonymous
    traffic. Should eventually be blocked by IPRateLimiter even though
    RequestRateLimiter never sees the same "user" twice.
    """
    print(f"\n=== Anonymous IP flood simulation (n={n}) ===")
    blocked = 0
    for i in range(n):
        resp = requests.get(f"{HOST}/api/products")
        status = "BLOCKED" if resp.status_code == 429 else "allowed"
        if status == "BLOCKED":
            blocked += 1
        print(f"  request {i + 1}: HTTP {resp.status_code} {status}")
    print(f"  {blocked}/{n} anonymous requests blocked by IP rate limit.")
    return blocked


def rotating_user_id_flood(n=35):
    """
    Burst of requests where X-User-Id is DIFFERENT on every request --
    simulates an attacker spoofing a new identity each time to dodge
    RequestRateLimiter. IPRateLimiter only triggers for anonymous
    requests, so this variant intentionally demonstrates the current
    boundary of what it catches.
    """
    print(f"\n=== Rotating user_id flood simulation (n={n}) ===")
    blocked = 0
    for i in range(n):
        resp = requests.get(
            f"{HOST}/api/products",
            headers={"X-User-Id": f"attacker_{i}", "X-User-Role": "user"},
        )
        status = "BLOCKED" if resp.status_code == 429 else "allowed"
        if status == "BLOCKED":
            blocked += 1
        print(f"  request {i + 1} (user_id=attacker_{i}): HTTP {resp.status_code} {status}")
    print(f"  {blocked}/{n} rotating-identity requests blocked.")
    print("  (Expected: 0 blocked -- this shows the gap IPRateLimiter does NOT")
    print("   cover, since it only runs for fully anonymous requests.)")
    return blocked


if __name__ == "__main__":
    anonymous_flood()
    rotating_user_id_flood()
