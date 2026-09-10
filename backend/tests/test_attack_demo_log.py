from pathlib import Path
from app.services.log_parser import parse_nginx_combined_line

def test_attack_demo_log_is_parseable_and_contains_security_signals():
    path = Path(__file__).resolve().parents[1] / "demo" / "attack.nginx.log"
    assert path.exists()
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    parsed = [parse_nginx_combined_line(line) for line in lines]
    assert len(parsed) >= 8
    assert any(item.status in {401,403,404} for item in parsed)
    assert any(any(token in item.path for token in ("/admin","/.env","/wp-admin","/.git")) for item in parsed)
