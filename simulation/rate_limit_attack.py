"""
rate_limit_attack.py

Simulates two abuse patterns the rate limiters should catch:

1. Burst flood - one user hammering a single endpoint fast (bot-style),
   caught by the volume rate limiter.
2. Slow scan - one user requesting many distinct order IDs slowly enough
   to dodge the volume limiter, but still caught by the business-flow
   limiter (see rate_limiter.py).

Usage:
    python -m simulation.rate_limit_attack
"""

import time
import requests

HOST = "http://localhost:8000"


def burst_flood(attacker="user_c", n=30):
    print(f"\n=== Burst flood simulation (attacker='{attacker}', n={n}) ===")
    blocked = 0
    for i in range(n):
        resp = requests.get(f"{HOST}/api/products",
                             headers={"X-User-Id": attacker, "X-User-Role": "user"})
        if resp.status_code == 429:
            blocked += 1
    print(f"  {blocked}/{n} requests blocked by volume rate limit.")
    return blocked


def slow_scan(attacker="user_a", n=8, delay=0.5):
    print(f"\n=== Slow object-scan simulation (attacker='{attacker}', n={n}) ===")
    blocked = 0
    for order_id in range(1001, 1001 + n):
        resp = requests.get(f"{HOST}/api/orders/{order_id}",
                             headers={"X-User-Id": attacker, "X-User-Role": "user"})
        status = "BLOCKED" if resp.status_code in (403, 429) else "allowed"
        if status == "BLOCKED":
            blocked += 1
        print(f"  order {order_id}: HTTP {resp.status_code} {status}")
        time.sleep(delay)
    print(f"  {blocked}/{n} slow-scan requests blocked.")
    return blocked


if __name__ == "__main__":
    burst_flood()
    slow_scan()