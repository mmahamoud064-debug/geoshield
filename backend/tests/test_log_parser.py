from datetime import timezone
import pytest
from app.services.log_parser import LogParseError, parse_nginx_combined_line

def test_parse_nginx_combined_line_extracts_security_fields():
    event=parse_nginx_combined_line('203.0.113.10 - - [07/Sep/2026:10:15:00 +0000] "GET /admin HTTP/1.1" 403 123 "-" "curl/8.0"')
    assert event.ip == "203.0.113.10"
    assert event.method == "GET"
    assert event.path == "/admin"
    assert event.status == 403
    assert event.timestamp.tzinfo is not None
    assert event.timestamp.utcoffset() == timezone.utc.utcoffset(event.timestamp)

def test_parse_nginx_combined_line_rejects_malformed_line():
    with pytest.raises(LogParseError):
        parse_nginx_combined_line("this is not a combined log line")
