from __future__ import annotations

from datetime import datetime
from ipaddress import ip_address
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EventCreate(BaseModel):
    timestamp: datetime | None = None
    ip: str
    method: str = Field(min_length=1, max_length=16)
    path: str = Field(min_length=1, max_length=4096)
    status: int = Field(ge=100, le=599)
    user_identifier: str | None = Field(default=None, max_length=128)
    session_identifier: str | None = Field(default=None, max_length=128)
    synthetic: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, value: str) -> str:
        try:
            ip_address(value)
        except ValueError as exc:
            raise ValueError("invalid IP address") from exc
        return value


class EventView(BaseModel):
    id: int
    timestamp: datetime
    ip: str
    method: str
    path: str
    status: int
    risk_score: int
    enrichment_status: str
    synthetic: bool
    country_code: str | None = None
    asn: str | None = None
    is_proxy: bool = False
