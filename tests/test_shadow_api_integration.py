from datetime import datetime

from api.database import Base, SessionLocal, engine
from api.models import APITraffic
from shadow_api.service import discover_shadow_apis


def setup_function():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        db.query(APITraffic).delete()
        db.commit()
    finally:
        db.close()


def teardown_function():
    db = SessionLocal()

    try:
        db.query(APITraffic).delete()
        db.commit()
    finally:
        db.close()


def test_shadow_discovery_generates_schema_and_classifies_apis():
    db = SessionLocal()

    try:
        db.add_all(
            [
                APITraffic(
                    timestamp=datetime.utcnow(),
                    method="GET",
                    path="/api/users/101",
                    host="example.local",
                    status_code=200,
                ),
                APITraffic(
                    timestamp=datetime.utcnow(),
                    method="POST",
                    path="/api/admin/users",
                    host="example.local",
                    status_code=201,
                ),
            ]
        )

        db.commit()

        official_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Official API",
                "version": "1.0.0",
            },
            "paths": {
                "/api/users/{id}": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "OK",
                            }
                        }
                    }
                },
                "/api/orders": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "OK",
                            }
                        }
                    },
                },
            },
        }

        result = discover_shadow_apis(
            db=db,
            official_spec=official_spec,
        )

        assert "GET /api/users/{id}" in result["known_apis"]

        assert "POST /api/admin/users" in result["shadow_apis"]

        assert "GET /api/orders" in result["zombie_apis"]

        assert result["count_known"] == 1
        assert result["count_shadow"] == 1
        assert result["count_zombie"] == 1

        generated_paths = result["observed_schema"]["paths"]

        assert "/api/users/{id}" in generated_paths
        assert "/api/admin/users" in generated_paths

    finally:
        db.close()


def test_shadow_discovery_handles_empty_traffic():
    db = SessionLocal()

    try:
        official_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Official API",
                "version": "1.0.0",
            },
            "paths": {
                "/api/health": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "OK",
                            }
                        }
                    }
                }
            },
        }

        result = discover_shadow_apis(
            db=db,
            official_spec=official_spec,
        )

        assert result["count_shadow"] == 0
        assert result["count_known"] == 0
        assert result["count_zombie"] == 1
        assert result["observed_schema"]["paths"] == {}

    finally:
        db.close()