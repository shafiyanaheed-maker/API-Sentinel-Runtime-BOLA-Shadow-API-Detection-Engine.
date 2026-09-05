import json

import pytest
import yaml

from shadow_api.detector import ShadowAPIDetector
from shadow_api.parser import extract_endpoints, load_openapi_spec
from shadow_api.traffic import (
    build_endpoint_signature,
    extract_observed_endpoints,
)


def test_extract_openapi_endpoints():
    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {},
                "post": {},
            },
            "/orders/{order_id}": {
                "get": {},
            },
        },
    }

    endpoints = extract_endpoints(spec)

    assert endpoints == {
        "GET /users",
        "POST /users",
        "GET /orders/{order_id}",
    }


def test_extract_endpoints_ignores_openapi_metadata():
    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {},
                "summary": "User endpoint",
                "parameters": [],
            }
        },
    }

    endpoints = extract_endpoints(spec)

    assert endpoints == {"GET /users"}


def test_load_json_openapi_spec(tmp_path):
    file_path = tmp_path / "openapi.json"

    specification = {
        "openapi": "3.0.0",
        "paths": {
            "/products": {
                "get": {},
            }
        },
    }

    file_path.write_text(
        json.dumps(specification),
        encoding="utf-8",
    )

    loaded = load_openapi_spec(file_path)

    assert loaded == specification


def test_load_yaml_openapi_spec(tmp_path):
    file_path = tmp_path / "openapi.yaml"

    specification = {
        "openapi": "3.0.0",
        "paths": {
            "/products": {
                "get": {},
            }
        },
    }

    file_path.write_text(
        yaml.safe_dump(specification),
        encoding="utf-8",
    )

    loaded = load_openapi_spec(file_path)

    assert loaded == specification


def test_build_endpoint_signature():
    assert build_endpoint_signature(
        "get",
        "/api/users",
    ) == "GET /api/users"


def test_extract_observed_endpoints():
    requests = [
        {"method": "GET", "path": "/api/users"},
        {"method": "POST", "path": "/api/orders"},
        {"method": "GET", "path": "/api/users"},
    ]

    endpoints = extract_observed_endpoints(requests)

    assert endpoints == {
        "GET /api/users",
        "POST /api/orders",
    }


def test_shadow_api_detection():
    documented = {
        "GET /api/users",
        "POST /api/orders",
    }

    observed = {
        "GET /api/users",
        "POST /api/orders",
        "GET /api/internal/debug",
    }

    result = ShadowAPIDetector().detect(
        documented,
        observed,
    )

    assert result["shadow_apis"] == [
        "GET /api/internal/debug"
    ]
    assert result["count_shadow"] == 1


def test_zombie_api_detection():
    documented = {
        "GET /api/users",
        "GET /api/legacy",
    }

    observed = {
        "GET /api/users",
    }

    result = ShadowAPIDetector().detect(
        documented,
        observed,
    )

    assert result["zombie_apis"] == [
        "GET /api/legacy"
    ]
    assert result["count_zombie"] == 1


def test_known_endpoints_are_identified():
    documented = {
        "GET /api/users",
    }

    observed = {
        "GET /api/users",
        "GET /api/debug",
    }

    result = ShadowAPIDetector().detect(
        documented,
        observed,
    )

    assert result["known_apis"] == [
        "GET /api/users"
    ]
    assert result["count_known"] == 1


def test_invalid_openapi_file_format(tmp_path):
    file_path = tmp_path / "openapi.txt"
    file_path.write_text("invalid", encoding="utf-8")

    with pytest.raises(ValueError):
        load_openapi_spec(file_path)


def test_missing_openapi_file():
    with pytest.raises(FileNotFoundError):
        load_openapi_spec("does-not-exist.yaml")