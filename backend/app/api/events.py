from __future__ import annotations

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_session
from app.models.entities import Event
from app.schemas.events import EventCreate, EventView
from app.services.ingestion import ingest_event
from app.services.log_parser import LogParseError, parse_nginx_combined_line


router = APIRouter(prefix="/api", tags=["events"])


def _to_view(event: Event) -> EventView:
    profile = event.ip_profile
    return EventView(
        id=event.id,
        timestamp=event.timestamp,
        ip=event.ip,
        method=event.method,
        path=event.path,
        status=event.status,
        risk_score=event.risk_score,
        enrichment_status=event.enrichment_status,
        synthetic=event.synthetic,
        country_code=profile.country_code if profile else None,
        asn=profile.asn if profile else None,
        is_proxy=bool(profile and profile.is_proxy),
    )


@router.post("/events", response_model=EventView, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, request: Request, session: Session = Depends(get_session)) -> EventView:
    event, _ = ingest_event(session, payload, request.app.state.ip_provider)
    return _to_view(event)


@router.get("/events", response_model=list[EventView])
def list_events(session: Session = Depends(get_session)) -> list[EventView]:
    events = session.scalars(
        select(Event).options(selectinload(Event.ip_profile)).order_by(Event.timestamp.desc(), Event.id.desc()).limit(200)
    ).all()
    return [_to_view(event) for event in events]


@router.post("/logs/upload")
async def upload_log(
    request: Request,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> dict[str, int]:
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        from fastapi import HTTPException
        raise HTTPException(status_code=413, detail="Log file is larger than 5 MB")

    processed = 0
    skipped = 0
    for raw_line in content.decode("utf-8", errors="replace").splitlines():
        if not raw_line.strip():
            continue
        try:
            parsed = parse_nginx_combined_line(raw_line)
        except LogParseError:
            skipped += 1
            continue

        payload = EventCreate(
            timestamp=parsed.timestamp,
            ip=parsed.ip,
            method=parsed.method,
            path=parsed.path,
            status=parsed.status,
            synthetic=False,
            metadata={"source": "nginx_upload", "user_agent": parsed.user_agent},
        )
        ingest_event(session, payload, request.app.state.ip_provider)
        processed += 1

    return {"processed": processed, "skipped": skipped}
