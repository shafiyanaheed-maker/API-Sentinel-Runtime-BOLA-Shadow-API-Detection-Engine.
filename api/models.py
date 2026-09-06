from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from api.database import Base


class APIEndpoint(Base):
    __tablename__ = "api_endpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    method: Mapped[str] = mapped_column(String(10), index=True)
    path: Mapped[str] = mapped_column(String(500), index=True)
    host: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # traffic = observed at runtime; openapi = supplied by official contract
    source: Mapped[str] = mapped_column(String(30), default="traffic")
    documented: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deprecated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    request_count: Mapped[int] = mapped_column(Integer, default=0)


class APITraffic(Base):
    __tablename__ = "api_traffic"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    method: Mapped[str] = mapped_column(String(10), index=True)
    path: Mapped[str] = mapped_column(String(500), index=True)
    host: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_ip: Mapped[str | None] = mapped_column(String(100), nullable=True)
    destination_ip: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    object_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    request_headers: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_headers: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)


class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    alert_type: Mapped[str] = mapped_column(String(100), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    object_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    source: Mapped[str] = mapped_column(String(50), default="detection-engine")
    status: Mapped[str] = mapped_column(String(30), default="open", index=True)
