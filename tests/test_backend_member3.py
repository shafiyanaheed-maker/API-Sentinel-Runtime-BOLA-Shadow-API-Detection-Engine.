from fastapi.testclient import TestClient

from api.database import init_db
from api.main import app


init_db()
client = TestClient(app)


def test_backend_health():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_traffic_ingestion_and_inventory():
    response = client.post(
        "/api/v1/traffic/ingest",
        json={
            "method": "GET",
            "path": "/users/101/orders/105",
            "host": "mock-api.local",
            "status_code": 200,
            "authenticated_user_id": 101,
            "user_role": "user",
            "request_headers": {
                "Authorization": "Bearer test-token"
            },
            "request_body": {},
            "response_body": {
                "order_id": 105
            },
            "latency_ms": 4.2,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["traffic_id"] > 0
    assert data["endpoint_id"] > 0

    inventory = client.get("/api/v1/inventory/endpoints")

    assert inventory.status_code == 200
    assert any(
        item["path"] == "/users/101/orders/105"
        for item in inventory.json()
    )


def test_alert_api():
    response = client.post(
        "/api/v1/alerts",
        json={
            "alert_type": "BOLA",
            "severity": "HIGH",
            "title": "Test BOLA alert",
            "description": "Test alert from backend API",
            "method": "GET",
            "path": "/orders/106",
        },
    )

    assert response.status_code == 200
    assert response.json()["alert_type"] == "BOLA"