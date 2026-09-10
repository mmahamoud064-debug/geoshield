from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RuleReason(BaseModel):
    rule: str
    points: int
    reason: str


class AlertView(BaseModel):
    id: int
    event_id: int
    severity: str
    score: int
    reasons: list[RuleReason]
    explanation: str
    created_at: datetime
    ip: str
    country_code: str | None = None


class IncidentEventView(BaseModel):
    timestamp: datetime
    method: str
    path: str
    status: int
    user_identifier: str | None = None
    session_identifier: str | None = None
    enrichment_status: str
    synthetic: bool


class IncidentNetworkView(BaseModel):
    country_code: str | None = None
    country_name: str | None = None
    region: str | None = None
    city: str | None = None
    asn: str | None = None
    isp: str | None = None
    is_proxy: bool = False
    proxy_type: str | None = None
    source: str | None = None


class IncidentTimelineItem(BaseModel):
    event_id: int
    timestamp: datetime
    method: str
    path: str
    status: int
    risk_score: int
    synthetic: bool


class AlertDetailView(AlertView):
    event: IncidentEventView
    network: IncidentNetworkView
    timeline: list[IncidentTimelineItem]
