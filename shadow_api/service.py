import json
from typing import Any

from sqlalchemy.orm import Session

from api.models import APIEndpoint, APITraffic
from shadow_api.detector import ShadowAPIDetector
from shadow_api.parser import extract_endpoints, normalize_path
from shadow_api.schema_generator import generate_openapi_schema


def _header_content_type(headers: str | None) -> str | None:
    """Extract Content-Type from stored JSON headers."""
    if not headers:
        return None

    try:
        parsed = json.loads(headers)
    except (TypeError, json.JSONDecodeError):
        return None

    if not isinstance(parsed, dict):
        return None

    for key, value in parsed.items():
        if str(key).lower() == "content-type":
            return str(value).split(";")[0].strip()

    return None


def _traffic_to_observed_request(traffic: APITraffic) -> dict[str, Any]:
    """Convert a database traffic record into schema-generator input."""
    return {
        "method": traffic.method,
        "path": traffic.path,
        "status_code": traffic.status_code,
        "request_content_type": _header_content_type(
            traffic.request_headers
        ),
        "response_content_type": _header_content_type(
            traffic.response_headers
        ),
    }


def generate_observed_openapi(
    db: Session,
    title: str = "API-Sentinel Observed APIs",
) -> dict[str, Any]:
    """Generate an OpenAPI schema from all stored API traffic."""
    traffic = (
        db.query(APITraffic)
        .order_by(APITraffic.timestamp.asc())
        .all()
    )

    observed_requests = [
        _traffic_to_observed_request(item)
        for item in traffic
    ]

    return generate_openapi_schema(
        observed_requests,
        title=title,
    )


def discover_shadow_apis(
    db: Session,
    official_spec: dict[str, Any],
    title: str = "API-Sentinel Observed APIs",
) -> dict[str, Any]:
    """
    Generate an observed OpenAPI schema and compare it with
    the official OpenAPI specification.
    """
    if not isinstance(official_spec, dict):
        raise ValueError("Official OpenAPI specification must be a dictionary.")

    documented_endpoints = extract_endpoints(official_spec)

    observed_schema = generate_observed_openapi(
        db,
        title=title,
    )

    observed_endpoints = extract_endpoints(observed_schema)

    detector = ShadowAPIDetector()
    result = detector.detect(
        documented_endpoints=documented_endpoints,
        observed_endpoints=observed_endpoints,
    )

    _sync_inventory(
        db=db,
        documented_endpoints=documented_endpoints,
        observed_endpoints=observed_endpoints,
        shadow_apis=set(result["shadow_apis"]),
    )

    result["observed_schema"] = observed_schema
    result["documented_endpoints"] = sorted(documented_endpoints)
    result["observed_endpoints"] = sorted(observed_endpoints)

    return result


def _sync_inventory(
    db: Session,
    documented_endpoints: set[str],
    observed_endpoints: set[str],
    shadow_apis: set[str],
) -> None:
    """
    Synchronize normalized discovery results into APIEndpoint inventory.
    """
    all_endpoints = documented_endpoints | observed_endpoints

    for signature in sorted(all_endpoints):
        method, raw_path = signature.split(" ", 1)
        path = normalize_path(raw_path)

        is_documented = signature in documented_endpoints
        is_observed = signature in observed_endpoints
        is_shadow = signature in shadow_apis

        endpoint = (
            db.query(APIEndpoint)
            .filter(
                APIEndpoint.method == method,
                APIEndpoint.path == path,
                APIEndpoint.host.is_(None),
            )
            .first()
        )

        if endpoint is None:
            endpoint = APIEndpoint(
                method=method,
                path=path,
                host=None,
                source="openapi-discovery",
                documented=is_documented,
                deprecated=False,
                request_count=1 if is_observed else 0,
            )
            db.add(endpoint)
        else:
            endpoint.documented = is_documented

            if is_observed:
                endpoint.request_count = max(
                    endpoint.request_count,
                    1,
                )

            if is_shadow:
                endpoint.source = "shadow-api-discovery"

            elif is_documented:
                endpoint.source = "openapi"

    db.commit()