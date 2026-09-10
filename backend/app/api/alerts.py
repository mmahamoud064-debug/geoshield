from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_session
from app.models.entities import Alert, Event
from app.schemas.alerts import (
    AlertDetailView,
    AlertView,
    IncidentEventView,
    IncidentNetworkView,
    IncidentTimelineItem,
)


router = APIRouter(prefix="/api", tags=["alerts"])


def _to_view(alert: Alert) -> AlertView:
    event = alert.event
    profile = event.ip_profile
    return AlertView(
        id=alert.id,
        event_id=alert.event_id,
        severity=alert.severity,
        score=alert.score,
        reasons=alert.contributions,
        explanation=alert.explanation,
        created_at=alert.created_at,
        ip=event.ip,
        country_code=profile.country_code if profile else None,
    )


def _alert_query():
    return select(Alert).options(joinedload(Alert.event).joinedload(Event.ip_profile))


@router.get("/alerts", response_model=list[AlertView])
def list_alerts(session: Session = Depends(get_session)) -> list[AlertView]:
    alerts = session.scalars(_alert_query().order_by(Alert.created_at.desc(), Alert.id.desc()).limit(200)).unique().all()
    return [_to_view(alert) for alert in alerts]


@router.get("/alerts/{alert_id}", response_model=AlertDetailView)
def get_alert(alert_id: int, session: Session = Depends(get_session)) -> AlertDetailView:
    alert = session.scalar(_alert_query().where(Alert.id == alert_id))
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    event = alert.event
    profile = event.ip_profile
    timeline_events = session.scalars(
        select(Event)
        .where(Event.ip == event.ip, Event.timestamp <= event.timestamp)
        .order_by(Event.timestamp.desc(), Event.id.desc())
        .limit(12)
    ).all()
    timeline_events.reverse()

    base = _to_view(alert)
    return AlertDetailView(
        **base.model_dump(),
        event=IncidentEventView(
            timestamp=event.timestamp,
            method=event.method,
            path=event.path,
            status=event.status,
            user_identifier=event.user_identifier,
            session_identifier=event.session_identifier,
            enrichment_status=event.enrichment_status,
            synthetic=event.synthetic,
        ),
        network=IncidentNetworkView(
            country_code=profile.country_code if profile else None,
            country_name=profile.country_name if profile else None,
            region=profile.region if profile else None,
            city=profile.city if profile else None,
            asn=profile.asn if profile else None,
            isp=profile.isp if profile else None,
            is_proxy=bool(profile and profile.is_proxy),
            proxy_type=profile.proxy_type if profile else None,
            source=profile.source if profile else None,
        ),
        timeline=[
            IncidentTimelineItem(
                event_id=item.id,
                timestamp=item.timestamp,
                method=item.method,
                path=item.path,
                status=item.status,
                risk_score=item.risk_score,
                synthetic=item.synthetic,
            )
            for item in timeline_events
        ],
    )


@router.get("/overview")
def overview(session: Session = Depends(get_session)) -> dict[str, int]:
    total_events = session.scalar(select(func.count(Event.id))) or 0
    unique_ips = session.scalar(select(func.count(func.distinct(Event.ip)))) or 0
    risky_events = session.scalar(select(func.count(Event.id)).where(Event.risk_score >= 30)) or 0
    active_alerts = session.scalar(select(func.count(Alert.id))) or 0
    return {
        "total_events": total_events,
        "unique_ips": unique_ips,
        "risky_events": risky_events,
        "active_alerts": active_alerts,
    }
