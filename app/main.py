"""
main.py

Standalone demo FastAPI app with the EnforcementMiddleware plugged in.
This is what you run to see the enforcement layer actually working against
real HTTP requests.

Run with: uvicorn app.main:app --reload --port 8000

Then test with curl or the attack simulation scripts.
"""

from typing import Optional

from fastapi import FastAPI, Query
from .blocking_middleware import EnforcementMiddleware
from .audit import audit_logger

app = FastAPI(title="API-Sentinel Enforcement Demo")
app.add_middleware(EnforcementMiddleware)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/products")
def list_products():
    return {"products": ["laptop", "phone", "headphones"]}


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    # In the real system, this would fetch from the database.
    # The middleware already checked BFLA and BOLA before we get here,
    # so if we reach this point, the request is authorized.
    return {
        "order_id": order_id,
        "status": "shipped",
        "note": "authorization already verified by middleware"
    }


@app.post("/api/admin/users")
def create_user():
    return {"status": "user created", "note": "admin endpoint"}


@app.post("/api/admin/refund")
def issue_refund():
    return {"status": "refund issued", "note": "admin endpoint"}


@app.get("/api/admin/audit")
def get_audit_log(
    user_id: Optional[str] = Query(default=None),
    allowed: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
):
    """
    Query the audit log. Filters:
      - user_id: only entries for this user
      - allowed: true = only allowed requests, false = only blocked requests
      - limit: max entries to return (default 50, max 500)
    """
    entries = audit_logger.query(user_id=user_id, allowed=allowed, limit=limit)
    return {
        "count": len(entries),
        "entries": [
            {
                "timestamp": e.timestamp,
                "user_id": e.user_id,
                "endpoint": e.endpoint,
                "method": e.method,
                "allowed": e.allowed,
                "reason": e.reason,
            }
            for e in entries
        ],
    }
