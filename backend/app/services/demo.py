from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import IPProfile
from app.schemas.events import EventCreate


_DEMO_PROFILES = [
    {
        "ip": "192.0.2.10",
        "country_code": "AU",
        "country_name": "Australia",
        "region": "Queensland",
        "city": "South Brisbane",
        "latitude": -27.47,
        "longitude": 153.02,
        "asn": "13335",
        "isp": "GeoShield Demo Network AU",
        "is_proxy": False,
        "proxy_type": None,
    },
    {
        "ip": "198.51.100.20",
        "country_code": "US",
        "country_name": "United States",
        "region": "California",
        "city": "Mountain View",
        "latitude": 37.38605,
        "longitude": -122.08385,
        "asn": "15169",
        "isp": "GeoShield Demo VPN Exit",
        "is_proxy": True,
        "proxy_type": "VPN",
    },
    {
        "ip": "203.0.113.30",
        "country_code": "DE",
        "country_name": "Germany",
        "region": "Hesse",
        "city": "Frankfurt",
        "latitude": 50.1109,
        "longitude": 8.6821,
        "asn": "19281",
        "isp": "GeoShield Demo Network DE",
        "is_proxy": False,
        "proxy_type": None,
    },
]


def seed_demo_profiles(session: Session) -> None:
    for values in _DEMO_PROFILES:
        existing = session.scalar(select(IPProfile).where(IPProfile.ip == values["ip"]))
        if existing is not None:
            continue
        session.add(
            IPProfile(
                **values,
                source="demo",
                raw_data={"synthetic": True, "source": "geoshield_demo_fixture"},
            )
        )
    session.flush()


def build_demo_events() -> list[EventCreate]:
    base = datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc)
    rows = [
        (0, "192.0.2.10", "GET", "/", 200),
        (2, "203.0.113.30", "GET", "/products", 200),
        (4, "192.0.2.10", "GET", "/docs", 200),
        (8, "198.51.100.20", "POST", "/admin/login", 401),
        (9, "198.51.100.20", "POST", "/admin/login", 401),
        (10, "198.51.100.20", "POST", "/admin/login", 401),
        (14, "203.0.113.30", "GET", "/.env", 404),
        (15, "203.0.113.30", "GET", "/wp-admin", 404),
        (16, "203.0.113.30", "GET", "/.git/config", 404),
        (20, "192.0.2.10", "GET", "/pricing", 200),
    ]
    return [
        EventCreate(
            timestamp=base + timedelta(seconds=offset),
            ip=ip,
            method=method,
            path=path,
            status=status,
            synthetic=True,
            metadata={"source": "geoshield_demo", "scenario": "contest_demo_v1"},
        )
        for offset, ip, method, path, status in rows
    ]
