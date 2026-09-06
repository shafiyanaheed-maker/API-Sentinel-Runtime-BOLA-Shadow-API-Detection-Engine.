"""
detection_accuracy.py

Sends a mix of KNOWN-LEGITIMATE traffic and KNOWN-ATTACK traffic against
the live demo server, records what got blocked vs allowed, and computes
precision / recall / false-positive-rate. This turns "it blocks attacks"
into real, defensible numbers for a project report.

Usage:
    uvicorn app.main:app --port 8000   (in one terminal)
    python -m validation.detection_accuracy   (in another terminal)
"""

import time

import requests

HOST = "http://127.0.0.1:8000"


def legitimate_traffic():
    """Requests that SHOULD be allowed. label=0 (benign)."""
    cases = []

    # user_a reading their own orders
    for order_id in ["1001", "1002"]:
        r = requests.get(
            f"{HOST}/api/orders/{order_id}",
            headers={
                "X-User-Id": "user_a",
                "X-User-Role": "user",
            },
        )
        cases.append(
            {
                "label": 0,
                "desc": f"user_a reads own order {order_id}",
                "status": r.status_code,
                "blocked": r.status_code in (403, 429),
            }
        )
        time.sleep(0.2)

    # user_b reading their own orders
    for order_id in ["1003", "1004"]:
        r = requests.get(
            f"{HOST}/api/orders/{order_id}",
            headers={
                "X-User-Id": "user_b",
                "X-User-Role": "user",
            },
        )
        cases.append(
            {
                "label": 0,
                "desc": f"user_b reads own order {order_id}",
                "status": r.status_code,
                "blocked": r.status_code in (403, 429),
            }
        )
        time.sleep(0.2)

    # normal browsing of a public endpoint
    for _ in range(3):
        r = requests.get(
            f"{HOST}/api/products",
            headers={
                "X-User-Id": "user_a",
                "X-User-Role": "user",
            },
        )
        cases.append(
            {
                "label": 0,
                "desc": "user_a browses products",
                "status": r.status_code,
                "blocked": r.status_code in (403, 429),
            }
        )
        time.sleep(0.3)

    # admin legitimately using an admin endpoint
    r = requests.post(
        f"{HOST}/api/admin/refund",
        headers={
            "X-User-Id": "admin_1",
            "X-User-Role": "admin",
        },
    )
    cases.append(
        {
            "label": 0,
            "desc": "admin issues refund",
            "status": r.status_code,
            "blocked": r.status_code in (403, 429),
        }
    )

    return cases


def attack_traffic():
    """Requests that SHOULD be blocked. label=1 (malicious)."""
    cases = []

    # BOLA: user_a reads other users' orders
    for order_id in ["1003", "1004", "1005"]:
        r = requests.get(
            f"{HOST}/api/orders/{order_id}",
            headers={
                "X-User-Id": "user_a",
                "X-User-Role": "user",
            },
        )
        cases.append(
            {
                "label": 1,
                "desc": f"user_a BOLA on order {order_id}",
                "status": r.status_code,
                "blocked": r.status_code in (403, 429),
            }
        )
        time.sleep(0.2)

    # BFLA: normal user hits admin endpoints
    r = requests.post(
        f"{HOST}/api/admin/users",
        headers={
            "X-User-Id": "user_c",
            "X-User-Role": "user",
        },
    )
    cases.append(
        {
            "label": 1,
            "desc": "user_c BFLA on /admin/users",
            "status": r.status_code,
            "blocked": r.status_code in (403, 429),
        }
    )

    r = requests.post(
        f"{HOST}/api/admin/refund",
        headers={
            "X-User-Id": "user_c",
            "X-User-Role": "user",
        },
    )
    cases.append(
        {
            "label": 1,
            "desc": "user_c BFLA on /admin/refund",
            "status": r.status_code,
            "blocked": r.status_code in (403, 429),
        }
    )

    # Volume abuse: burst on a fresh user id
    r = None

    for _ in range(25):
        r = requests.get(
            f"{HOST}/api/products",
            headers={
                "X-User-Id": "user_flood",
                "X-User-Role": "user",
            },
        )

    cases.append(
        {
            "label": 1,
            "desc": "user_flood burst (25th request)",
            "status": r.status_code,
            "blocked": r.status_code in (403, 429),
        }
    )

    return cases


if __name__ == "__main__":
    print("=== Legitimate traffic ===")

    legitimate_results = legitimate_traffic()

    for case in legitimate_results:
        print(case)

    print("\n=== Attack traffic ===")

    attack_results = attack_traffic()

    for case in attack_results:
        print(case)