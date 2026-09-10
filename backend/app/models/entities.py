from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IPProfile(Base):
    __tablename__ = "ip_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(String(45), unique=True, index=True)
    country_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    country_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    asn: Mapped[str | None] = mapped_column(String(64), nullable=True)
    isp: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_proxy: Mapped[bool] = mapped_column(Boolean, default=False)
    proxy_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="ip2location")
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    enriched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    events: Mapped[list[Event]] = relationship(back_populates="ip_profile")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ip: Mapped[str] = mapped_column(String(45), index=True)
    method: Mapped[str] = mapped_column(String(16))
    path: Mapped[str] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer, index=True)
    user_identifier: Mapped[str | None] = mapped_column(String(128), nullable=True)
    session_identifier: Mapped[str | None] = mapped_column(String(128), nullable=True)
    enrichment_status: Mapped[str] = mapped_column(String(32), default="pending")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ip_profile_id: Mapped[int | None] = mapped_column(ForeignKey("ip_profiles.id"), nullable=True)

    ip_profile: Mapped[IPProfile | None] = relationship(back_populates="events")
    alerts: Mapped[list[Alert]] = relationship(back_populates="event", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    score: Mapped[int] = mapped_column(Integer)
    contributions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    event: Mapped[Event] = relationship(back_populates="alerts")
