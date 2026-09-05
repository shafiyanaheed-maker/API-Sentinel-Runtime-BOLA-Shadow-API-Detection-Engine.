"""
bfla_attack.py

Simulates a Broken Function Level Authorization attack: a regular
("user" role) account tries to call admin-only endpoints directly.

Usage:
    python -m simulation.bfla_attack
"""

import requests

HOST = "http://localhost:8000"
ATTACKER = "user_b"  # a normal user, NOT an admin

ADMIN_ENDPOINTS = [
    ("POST", "/api/admin/users"),
    ("POST", "/api/admin/refund"),
]


def run():
    print(f"\n=== BFLA attack simulation (attacker='{ATTACKER}', role='user') ===")
    results = []

    for method, path in ADMIN_ENDPOINTS:
        resp = requests.request(
            method, f"{HOST}{path}",
            headers={"X-User-Id": ATTACKER, "X-User-Role": "user"},
        )
        blocked = resp.status_code in (403, 429)
        results.append((path, resp.status_code, blocked))
        print(f"  {method} {path}: HTTP {resp.status_code} "
              f"{'BLOCKED' if blocked else 'allowed'}")

    blocked_count = sum(1 for _, _, b in results if b)
    print(f"\n{blocked_count}/{len(results)} privilege-escalation attempts were blocked.")
    return results


if __name__ == "__main__":
    run()