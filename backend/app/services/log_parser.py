from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re


class LogParseError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ParsedLogEvent:
    timestamp: datetime
    ip: str
    method: str
    path: str
    status: int
    user_agent: str | None = None


_COMBINED = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+)(?: [^"]+)?" '
    r'(?P<status>\d{3}) \S+ "[^"]*" "(?P<user_agent>[^"]*)"$'
)


def parse_nginx_combined_line(line: str) -> ParsedLogEvent:
    match = _COMBINED.match(line.strip())
    if match is None:
        raise LogParseError("Malformed Nginx combined log line")

    try:
        timestamp = datetime.strptime(match.group("timestamp"), "%d/%b/%Y:%H:%M:%S %z")
        status = int(match.group("status"))
    except ValueError as exc:
        raise LogParseError("Invalid timestamp or status in log line") from exc

    return ParsedLogEvent(
        timestamp=timestamp,
        ip=match.group("ip"),
        method=match.group("method"),
        path=match.group("path"),
        status=status,
        user_agent=match.group("user_agent") or None,
    )
