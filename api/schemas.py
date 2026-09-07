from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class TrafficEvent(BaseModel):
    timestamp: datetime | None = None
    method: str = Field(..., min_length=1, max_length=10)
    path: str = Field(..., min_length=1, max_length=500)
    host: str | None = None

    status_code: int | None = None
    source_ip: str | None = None
    destination_ip: str | None = None

    # Optional authentication context lets the backend connect
    # observed traffic with the existing BOLA/BFLA detection engine.
    authenticated_user_id: int | None = None
    user_role: str | None = None

    request_headers: dict[str, Any] = Field(default_factory=dict)
    request_body: Any = None
    response_headers: dict[str, Any] = Field(default_factory=dict)
    response_body: Any = None

    latency_ms: float | None = None


class TrafficIngestResponse(BaseModel):
    traffic_id: int
    endpoint_id: int
    alerts_created: int
    message: str


class EndpointCreate(BaseModel):
    method: str = Field(..., min_length=1, max_length=10)
    path: str = Field(..., min_length=1, max_length=500)
    host: str | None = None
    documented: bool = False
    deprecated: bool = False
    source: str = "traffic"


class EndpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    method: str
    path: str
    host: str | None
    source: str
    documented: bool
    deprecated: bool
    first_seen: datetime
    last_seen: datetime
    request_count: int


class AlertCreate(BaseModel):
    alert_type: str
    severity: str = "MEDIUM"
    title: str
    description: str | None = None
    method: str | None = None
    path: str | None = None
    user_id: str | None = None
    object_id: str | None = None
    source: str = "detection-engine"


class AlertResponse(AlertCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    status: str
