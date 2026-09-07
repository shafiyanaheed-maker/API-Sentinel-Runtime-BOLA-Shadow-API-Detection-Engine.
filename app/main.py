"""
main.py

Standalone demo FastAPI app with the EnforcementMiddleware plugged in.
This is what you run to see the enforcement layer actually working against
real HTTP requests.

Run with: uvicorn app.main:app --reload --port 8000

Then test with curl or the attack simulation scripts.
"""

from fastapi import FastAPI
from .blocking_middleware import EnforcementMiddleware

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