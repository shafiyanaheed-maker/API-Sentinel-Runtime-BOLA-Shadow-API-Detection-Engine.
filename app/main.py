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
from pydantic import BaseModel
from starlette.responses import JSONResponse

from .blocking_middleware import EnforcementMiddleware
from .audit import audit_logger
from .alerts import alert_manager
from .access_control import access_control

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


@app.get("/api/admin/stats")
def get_stats():
    """
    Summary stats for the admin dashboard: alert counts by violation
    type, recent alerts, and audit log totals (allowed vs blocked).
    """
    alert_stats = alert_manager.get_stats()

    total_requests = len(audit_logger.query(limit=100000))
    blocked_requests = len(audit_logger.query(allowed=False, limit=100000))
    allowed_requests = total_requests - blocked_requests

    return {
        "alerts": alert_stats,
        "requests": {
            "total": total_requests,
            "allowed": allowed_requests,
            "blocked": blocked_requests,
        },
    }


class AccessControlRequest(BaseModel):
    entity_type: str  # "user" or "ip"
    value: str


@app.get("/api/admin/access-control")
def get_access_control_lists():
    """Current allowlist/blocklist contents."""
    return access_control.snapshot()


@app.post("/api/admin/blocklist")
def add_to_blocklist(body: AccessControlRequest):
    if body.entity_type == "user":
        access_control.block_user(body.value)
    elif body.entity_type == "ip":
        access_control.block_ip(body.value)
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "entity_type must be 'user' or 'ip'"},
        )
    return {"status": "blocked", "entity_type": body.entity_type, "value": body.value}


@app.delete("/api/admin/blocklist")
def remove_from_blocklist(body: AccessControlRequest):
    if body.entity_type == "user":
        access_control.unblock_user(body.value)
    elif body.entity_type == "ip":
        access_control.unblock_ip(body.value)
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "entity_type must be 'user' or 'ip'"},
        )
    return {"status": "unblocked", "entity_type": body.entity_type, "value": body.value}


@app.post("/api/admin/allowlist")
def add_to_allowlist(body: AccessControlRequest):
    if body.entity_type == "user":
        access_control.allow_user(body.value)
    elif body.entity_type == "ip":
        access_control.allow_ip(body.value)
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "entity_type must be 'user' or 'ip'"},
        )
    return {"status": "allowed", "entity_type": body.entity_type, "value": body.value}


@app.delete("/api/admin/allowlist")
def remove_from_allowlist(body: AccessControlRequest):
    if body.entity_type == "user":
        access_control.unallow_user(body.value)
    elif body.entity_type == "ip":
        access_control.unallow_ip(body.value)
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "entity_type must be 'user' or 'ip'"},
        )
    return {"status": "unallowed", "entity_type": body.entity_type, "value": body.value}
