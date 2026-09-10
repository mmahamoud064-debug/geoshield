from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.entities import Alert, Event, IPProfile
from app.risk.engine import RiskContext, evaluate_risk
from app.schemas.events import EventCreate
from app.services.ip_intelligence import IPIntelligenceError, IPIntelligenceProvider, enrich_ip


RECENT_WINDOW = timedelta(minutes=5)
COUNTRY_BASELINE_WINDOW = timedelta(minutes=30)
MIN_COUNTRY_BASELINE_EVENTS = 8
IMPOSSIBLE_TRAVEL_MIN_DISTANCE_KM = 500.0
IMPOSSIBLE_TRAVEL_SPEED_KMH = 900.0


def _recent_counts(session: Session, payload: EventCreate, at: datetime) -> tuple[int, int]:
    since = at - RECENT_WINDOW
    base = select(Event).where(Event.timestamp >= since, Event.timestamp <= at, Event.ip == payload.ip)
    request_count = session.scalar(select(func.count()).select_from(base.subquery())) or 0
    failed_count = session.scalar(
        select(func.count()).select_from(base.where(Event.status.in_([401, 403, 404])).subquery())
    ) or 0
    return request_count + 1, failed_count + (1 if payload.status in {401, 403, 404} else 0)


def _asn_burst_count(session: Session, profile: IPProfile | None, at: datetime, current_ip: str) -> int:
    if profile is None or not profile.asn:
        return 0

    since = at - RECENT_WINDOW
    existing_ips = set(
        session.scalars(
            select(Event.ip)
            .join(IPProfile, Event.ip_profile_id == IPProfile.id)
            .where(Event.timestamp >= since, Event.timestamp <= at, IPProfile.asn == profile.asn)
            .distinct()
        ).all()
    )
    existing_ips.add(current_ip)
    return len(existing_ips)


def _country_is_unusual(session: Session, profile: IPProfile | None, at: datetime) -> bool:
    if profile is None or not profile.country_code:
        return False

    since = at - COUNTRY_BASELINE_WINDOW
    countries = session.scalars(
        select(IPProfile.country_code)
        .join(Event, Event.ip_profile_id == IPProfile.id)
        .where(
            Event.timestamp >= since,
            Event.timestamp <= at,
            IPProfile.country_code.is_not(None),
        )
    ).all()
    countries = [country for country in countries if country]
    if len(countries) < MIN_COUNTRY_BASELINE_EVENTS:
        return False

    counts = Counter(countries)
    dominant_count = counts.most_common(1)[0][1]
    dominant_share = dominant_count / len(countries)
    return profile.country_code not in counts and dominant_share >= 0.60


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0088
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(a))


def _is_impossible_travel(
    session: Session,
    payload: EventCreate,
    profile: IPProfile | None,
    at: datetime,
) -> bool:
    if not payload.user_identifier or profile is None:
        return False
    if profile.latitude is None or profile.longitude is None:
        return False

    previous = session.scalar(
        select(Event)
        .options(joinedload(Event.ip_profile))
        .where(
            Event.user_identifier == payload.user_identifier,
            Event.timestamp < at,
        )
        .order_by(Event.timestamp.desc(), Event.id.desc())
        .limit(1)
    )
    if previous is None or previous.ip_profile is None:
        return False
    previous_profile = previous.ip_profile
    if previous_profile.latitude is None or previous_profile.longitude is None:
        return False

    elapsed_seconds = (_as_utc(at) - _as_utc(previous.timestamp)).total_seconds()
    if elapsed_seconds <= 0:
        return False

    distance_km = _haversine_km(
        previous_profile.latitude,
        previous_profile.longitude,
        profile.latitude,
        profile.longitude,
    )
    if distance_km < IMPOSSIBLE_TRAVEL_MIN_DISTANCE_KM:
        return False

    speed_kmh = distance_km / (elapsed_seconds / 3600)
    return speed_kmh > IMPOSSIBLE_TRAVEL_SPEED_KMH


def ingest_event(
    session: Session,
    payload: EventCreate,
    provider: IPIntelligenceProvider,
) -> tuple[Event, Alert | None]:
    timestamp = payload.timestamp or datetime.now(timezone.utc)
    profile: IPProfile | None = None
    enrichment_status = "complete"

    try:
        profile = enrich_ip(session, payload.ip, provider, allow_demo_cache=payload.synthetic)
    except IPIntelligenceError:
        enrichment_status = "failed"

    request_count, failed_count = _recent_counts(session, payload, timestamp)
    asn_burst_count = _asn_burst_count(session, profile, timestamp, payload.ip)
    country_is_unusual = _country_is_unusual(session, profile, timestamp)
    impossible_travel = _is_impossible_travel(session, payload, profile, timestamp)

    assessment = evaluate_risk(
        RiskContext(
            path=payload.path,
            status=payload.status,
            is_proxy=bool(profile and profile.is_proxy),
            recent_request_count=request_count,
            recent_failed_count=failed_count,
            country_is_unusual=country_is_unusual,
            asn_burst_count=asn_burst_count,
            impossible_travel=impossible_travel,
        )
    )

    event = Event(
        timestamp=timestamp,
        ip=payload.ip,
        method=payload.method.upper(),
        path=payload.path,
        status=payload.status,
        user_identifier=payload.user_identifier,
        session_identifier=payload.session_identifier,
        enrichment_status=enrichment_status,
        risk_score=assessment.score,
        synthetic=payload.synthetic,
        raw_metadata=payload.metadata,
        ip_profile=profile,
    )
    session.add(event)
    session.flush()

    alert: Alert | None = None
    if assessment.score >= 30:
        contributions = [
            {"rule": item.rule, "points": item.points, "reason": item.reason}
            for item in assessment.contributions
        ]
        alert = Alert(
            event=event,
            severity=assessment.severity,
            score=assessment.score,
            contributions=contributions,
            explanation=" ".join(item.reason for item in assessment.contributions),
        )
        session.add(alert)

    session.commit()
    session.refresh(event)
    if alert is not None:
        session.refresh(alert)
    return event, alert
