from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import APIEndpoint, APITraffic, SecurityAlert
from api.schemas import (
    AlertCreate,
    AlertResponse,
    EndpointCreate,
    EndpointResponse,
    TrafficEvent,
    TrafficIngestResponse,
)
from api.services import ingest_traffic

router = APIRouter(prefix="/api/v1", tags=["API-Sentinel Backend"])


@router.post("/traffic/ingest", response_model=TrafficIngestResponse)
def ingest(event: TrafficEvent, db: Session = Depends(get_db)):
    traffic, endpoint, alerts = ingest_traffic(db, event)
    return TrafficIngestResponse(
        traffic_id=traffic.id,
        endpoint_id=endpoint.id,
        alerts_created=len(alerts),
        message="API traffic ingested successfully",
    )


@router.post("/traffic/ingest/batch")
def ingest_batch(
    events: list[TrafficEvent],
    db: Session = Depends(get_db),
):
    results = []
    for event in events:
        traffic, endpoint, alerts = ingest_traffic(db, event)
        results.append({
            "traffic_id": traffic.id,
            "endpoint_id": endpoint.id,
            "alerts_created": len(alerts),
        })

    return {"count": len(results), "results": results}


@router.get("/traffic")
def list_traffic(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    return (
        db.query(APITraffic)
        .order_by(APITraffic.timestamp.desc())
        .limit(limit)
        .all()
    )


@router.get("/inventory/endpoints", response_model=list[EndpointResponse])
def list_endpoints(
    documented: bool | None = None,
    deprecated: bool | None = None,
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(APIEndpoint)

    if documented is not None:
        query = query.filter(APIEndpoint.documented == documented)
    if deprecated is not None:
        query = query.filter(APIEndpoint.deprecated == deprecated)

    return (
        query.order_by(APIEndpoint.last_seen.desc())
        .limit(limit)
        .all()
    )


@router.get("/inventory/shadow-apis", response_model=list[EndpointResponse])
def shadow_apis(
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    # Team Member 4's discovery logic can later refine this classification.
    return (
        db.query(APIEndpoint)
        .filter(APIEndpoint.documented.is_(False))
        .order_by(APIEndpoint.last_seen.desc())
        .limit(limit)
        .all()
    )


@router.post("/inventory/endpoints", response_model=EndpointResponse)
def upsert_endpoint(
    endpoint_data: EndpointCreate,
    db: Session = Depends(get_db),
):
    method = endpoint_data.method.upper()

    endpoint = (
        db.query(APIEndpoint)
        .filter(
            APIEndpoint.method == method,
            APIEndpoint.path == endpoint_data.path,
            APIEndpoint.host == endpoint_data.host,
        )
        .first()
    )

    if endpoint is None:
        endpoint = APIEndpoint(
            method=method,
            path=endpoint_data.path,
            host=endpoint_data.host,
            source=endpoint_data.source,
            documented=endpoint_data.documented,
            deprecated=endpoint_data.deprecated,
        )
        db.add(endpoint)
    else:
        endpoint.documented = endpoint_data.documented
        endpoint.deprecated = endpoint_data.deprecated
        endpoint.source = endpoint_data.source

    db.commit()
    db.refresh(endpoint)
    return endpoint


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(SecurityAlert)

    if status:
        query = query.filter(SecurityAlert.status == status)
    if severity:
        query = query.filter(SecurityAlert.severity == severity)

    return (
        query.order_by(SecurityAlert.timestamp.desc())
        .limit(limit)
        .all()
    )


@router.post("/alerts", response_model=AlertResponse)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
):
    alert = SecurityAlert(**alert_data.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/alerts/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    allowed = {"open", "investigating", "resolved", "false_positive"}

    if status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Use one of: {sorted(allowed)}",
        )

    alert = (
        db.query(SecurityAlert)
        .filter(SecurityAlert.id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = status
    db.commit()
    db.refresh(alert)
    return alert
