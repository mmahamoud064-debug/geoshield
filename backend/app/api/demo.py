from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.services.demo import build_demo_events, seed_demo_profiles
from app.services.ingestion import ingest_event


router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/sample-log", response_class=FileResponse)
def sample_attack_log() -> FileResponse:
    path = Path(__file__).resolve().parents[2] / "demo" / "attack.nginx.log"
    return FileResponse(path, media_type="text/plain", filename="geoshield-attack-demo.nginx.log")


@router.post("/start")
def start_demo(request: Request, session: Session = Depends(get_session)) -> dict[str, int | str]:
    seed_demo_profiles(session)
    alerts_created = 0
    events = build_demo_events()
    for payload in events:
        _, alert = ingest_event(session, payload, request.app.state.ip_provider)
        alerts_created += int(alert is not None)

    return {
        "mode": "synthetic",
        "synthetic_events": len(events),
        "alerts_created": alerts_created,
    }
