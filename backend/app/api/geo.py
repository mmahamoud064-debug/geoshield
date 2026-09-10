from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.models.entities import Event, IPProfile


router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.get("/activity")
def geo_activity(session: Session = Depends(get_session)) -> list[dict[str, int | float | str | None]]:
    rows = session.execute(
        select(
            IPProfile.country_code,
            IPProfile.country_name,
            IPProfile.latitude,
            IPProfile.longitude,
            func.count(Event.id).label("event_count"),
            func.sum(case((Event.risk_score >= 30, 1), else_=0)).label("risky_count"),
        )
        .join(Event, Event.ip_profile_id == IPProfile.id)
        .where(IPProfile.latitude.is_not(None), IPProfile.longitude.is_not(None))
        .group_by(
            IPProfile.country_code,
            IPProfile.country_name,
            IPProfile.latitude,
            IPProfile.longitude,
        )
        .order_by(func.count(Event.id).desc())
    ).all()

    return [
        {
            "country_code": row.country_code,
            "country_name": row.country_name,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "event_count": int(row.event_count or 0),
            "risky_count": int(row.risky_count or 0),
        }
        for row in rows
    ]
