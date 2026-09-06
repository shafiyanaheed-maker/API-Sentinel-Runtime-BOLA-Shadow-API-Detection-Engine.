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


def compute_metrics(cases):
    """
    Builds a confusion matrix from labelled results and computes
    precision, recall, F1, and false-positive rate.
    """
    tp = sum(
        1
        for c in cases
        if c["label"] == 1 and c["blocked"]
    )

    fn = sum(
        1
        for c in cases
        if c["label"] == 1 and not c["blocked"]
    )

    fp = sum(
        1
        for c in cases
        if c["label"] == 0 and c["blocked"]
    )

    tn = sum(
        1
        for c in cases
        if c["label"] == 0 and not c["blocked"]
    )

    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None
        and recall is not None
        and (precision + recall)
        else None
    )

    fpr = fp / (fp + tn) if (fp + tn) else None

    return {
        "true_positives": tp,
        "false_negatives": fn,
        "false_positives": fp,
        "true_negatives": tn,
        "precision": round(precision, 3)
        if precision is not None
        else None,
        "recall": round(recall, 3)
        if recall is not None
        else None,
        "f1_score": round(f1, 3)
        if f1 is not None
        else None,
        "false_positive_rate": round(fpr, 3)
        if fpr is not None
        else None,
    }


def main():
    """Run legitimate and attack traffic and print the accuracy report."""
    legit = legitimate_traffic()
    attacks = attack_traffic()

    all_cases = legit + attacks
    metrics = compute_metrics(all_cases)

    print("\n=== Detection Accuracy Report ===")

    for c in all_cases:
        label = "ATTACK" if c["label"] == 1 else "legit "
        outcome = "BLOCKED" if c["blocked"] else "allowed"
        correct = (c["label"] == 1) == c["blocked"]
        mark = "OK" if correct else "WRONG"

        print(
            f"  [{label}] "
            f"{c['desc']:<35} -> "
            f"HTTP {c['status']} "
            f"{outcome:8} "
            f"[{mark}]"
        )

    print("\n--- Confusion Matrix ---")
    print(f"  True Positives : {metrics['true_positives']}")
    print(f"  False Positives: {metrics['false_positives']}")
    print(f"  True Negatives : {metrics['true_negatives']}")
    print(f"  False Negatives: {metrics['false_negatives']}")

    print("\n--- Metrics ---")
    for key, value in metrics.items():
        if key not in {
            "true_positives",
            "false_negatives",
            "false_positives",
            "true_negatives",
        }:
            print(f"  {key}: {value}")

    return {
        "cases": all_cases,
        "metrics": metrics,
    }


if __name__ == "__main__":
    main()