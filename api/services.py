import json

from sqlalchemy.orm import Session

from api.models import APIEndpoint, APITraffic, SecurityAlert
from api.parser import (
    extract_user_object_ids,
    mask_headers,
    normalize_path,
    serialize_body,
)
from api.schemas import TrafficEvent

from runtime.analyzer import analyze_request
from runtime.models import APIRequest


def _severity_from_threat(threat: dict) -> str:
    return str(threat.get("severity", "MEDIUM")).upper()


def _alert_from_threat(
    db: Session,
    threat: dict,
    event: TrafficEvent,
    user_id: str | None,
    object_id: str | None,
) -> SecurityAlert:
    alert_type = str(threat.get("type", "API_SECURITY"))
    title = {
        "BOLA": "Broken Object Level Authorization detected",
        "BFLA": "Broken Function Level Authorization detected",
    }.get(alert_type, "API security threat detected")

    description = threat.get("reason", "Runtime security anomaly detected")

    alert = SecurityAlert(
        alert_type=alert_type,
        severity=_severity_from_threat(threat),
        title=title,
        description=description,
        method=event.method.upper(),
        path=normalize_path(event.path),
        user_id=user_id,
        object_id=object_id,
        source="runtime-detection-engine",
        status="open",
    )
    db.add(alert)
    return alert


def ingest_traffic(db: Session, event: TrafficEvent):
    path = normalize_path(event.path)
    user_id, object_id = extract_user_object_ids(
        path, event.request_body, event.request_headers
    )

    # Prefer explicit authentication context supplied by the collector.
    if event.authenticated_user_id is not None:
        user_id = str(event.authenticated_user_id)

    traffic = APITraffic(
        timestamp=event.timestamp,
        method=event.method.upper(),
        path=path,
        host=event.host,
        status_code=event.status_code,
        source_ip=event.source_ip,
        destination_ip=event.destination_ip,
        user_id=user_id,
        object_id=object_id,
        request_headers=json.dumps(mask_headers(event.request_headers)),
        request_body=serialize_body(event.request_body),
        response_headers=json.dumps(mask_headers(event.response_headers)),
        response_body=serialize_body(event.response_body),
        latency_ms=event.latency_ms,
    )
    db.add(traffic)

    endpoint = (
        db.query(APIEndpoint)
        .filter(
            APIEndpoint.method == event.method.upper(),
            APIEndpoint.path == path,
            APIEndpoint.host == event.host,
        )
        .first()
    )

    if endpoint is None:
        endpoint = APIEndpoint(
            method=event.method.upper(),
            path=path,
            host=event.host,
            source="traffic",
            documented=False,
            deprecated=False,
            request_count=1,
        )
        db.add(endpoint)
    else:
        endpoint.request_count += 1

    alerts = []

    # Connect the Team Member 3 ingestion layer to the existing
    # Team Member 1/5 runtime BOLA/BFLA engine when auth context exists.
    if event.authenticated_user_id is not None and event.user_role:
        result = analyze_request(
            APIRequest(
                method=event.method,
                path=path,
                authenticated_user_id=event.authenticated_user_id,
                user_role=event.user_role,
            )
        )

        for threat in result.threats:
            alerts.append(
                _alert_from_threat(
                    db, threat, event, user_id, object_id
                )
            )

    db.commit()
    db.refresh(traffic)
    db.refresh(endpoint)

    return traffic, endpoint, alerts
