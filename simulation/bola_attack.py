"""
bola_attack.py

Simulates a Broken Object Level Authorization attack: a logged-in user
tries to read order records belonging to OTHER users by simply
incrementing the order_id in the URL.

Run this against the demo server (uvicorn app.main:app --port 8000)
to see enforcement block the cross-owner reads.

Usage:
    python -m simulation.bola_attack
"""

import time
import requests

HOST = "http://localhost:8000"
ATTACKER = "user_a"  # legitimately owns orders 1001, 1002 only


def run():
    print(f"\n=== BOLA attack simulation (attacker='{ATTACKER}') ===")
    results = []

    for order_id in [str(i) for i in range(1001, 1006)]:
        resp = requests.get(
            f"{HOST}/api/orders/{order_id}",
            headers={"X-User-Id": ATTACKER, "X-User-Role": "user"},
        )
        blocked = resp.status_code in (403, 429)
        results.append((order_id, resp.status_code, blocked))
        print(f"  order {order_id}: HTTP {resp.status_code} "
              f"{'BLOCKED' if blocked else 'allowed'}")
        time.sleep(0.1)

    blocked_count = sum(1 for _, _, b in results if b)
    print(f"\n{blocked_count}/{len(results)} requests were blocked.")
    return results


if __name__ == "__main__":
    run()