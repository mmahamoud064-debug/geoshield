from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import ip_address
from os import getenv
from typing import Any, Protocol

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import IPProfile


class IPIntelligenceError(RuntimeError):
    pass


@dataclass(slots=True)
class IPIntelResult:
    ip: str
    country_code: str | None = None
    country_name: str | None = None
    region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    asn: str | None = None
    isp: str | None = None
    is_proxy: bool = False
    proxy_type: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


class IPIntelligenceProvider(Protocol):
    def lookup(self, ip: str) -> IPIntelResult: ...


def is_external_lookup_allowed(ip: str) -> bool:
    try:
        parsed = ip_address(ip)
    except ValueError:
        return False
    return parsed.is_global


class IP2LocationHTTPProvider:
    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        timeout_seconds: float = 5.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else getenv("IP2LOCATION_API_KEY", "")
        self.api_url = api_url or getenv("IP2LOCATION_API_URL", "https://api.ip2location.io/")
        self.timeout_seconds = timeout_seconds
        self.client = client

    def lookup(self, ip: str) -> IPIntelResult:
        params = {"ip": ip, "format": "json"}
        if self.api_key:
            params["key"] = self.api_key

        try:
            client = self.client or httpx.Client(timeout=self.timeout_seconds)
            response = client.get(self.api_url, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise IPIntelligenceError(f"IP2Location lookup failed for {ip}") from exc
        finally:
            if self.client is None and "client" in locals():
                client.close()

        if isinstance(payload, dict) and payload.get("error"):
            error = payload["error"]
            message = error.get("error_message") if isinstance(error, dict) else str(error)
            raise IPIntelligenceError(message or f"IP2Location lookup failed for {ip}")

        proxy = payload.get("proxy") if isinstance(payload.get("proxy"), dict) else {}
        return IPIntelResult(
            ip=payload.get("ip", ip),
            country_code=payload.get("country_code"),
            country_name=payload.get("country_name"),
            region=payload.get("region_name"),
            city=payload.get("city_name"),
            latitude=payload.get("latitude"),
            longitude=payload.get("longitude"),
            asn=str(payload["asn"]) if payload.get("asn") is not None else None,
            isp=payload.get("isp") or payload.get("as"),
            is_proxy=bool(payload.get("is_proxy", proxy.get("is_proxy", False))),
            proxy_type=proxy.get("proxy_type") or payload.get("proxy_type"),
            raw_data=payload,
        )


def _apply_result(profile: IPProfile, result: IPIntelResult) -> None:
    profile.country_code = result.country_code
    profile.country_name = result.country_name
    profile.region = result.region
    profile.city = result.city
    profile.latitude = result.latitude
    profile.longitude = result.longitude
    profile.asn = result.asn
    profile.isp = result.isp
    profile.is_proxy = result.is_proxy
    profile.proxy_type = result.proxy_type
    profile.source = "ip2location"
    profile.raw_data = result.raw_data


def enrich_ip(
    session: Session,
    ip: str,
    provider: IPIntelligenceProvider,
    *,
    allow_demo_cache: bool = True,
) -> IPProfile:
    cached = session.scalar(select(IPProfile).where(IPProfile.ip == ip))
    if cached is not None and (cached.source != "demo" or allow_demo_cache):
        return cached

    if not is_external_lookup_allowed(ip):
        if cached is not None:
            cached.source = "local"
            cached.raw_data = {"external_lookup": False}
            cached.is_proxy = False
            cached.proxy_type = None
            session.flush()
            return cached
        profile = IPProfile(ip=ip, source="local", raw_data={"external_lookup": False})
    else:
        result = provider.lookup(ip)
        if cached is not None:
            _apply_result(cached, result)
            session.flush()
            return cached
        profile = IPProfile(ip=ip)
        _apply_result(profile, result)

    session.add(profile)
    session.flush()
    return profile
