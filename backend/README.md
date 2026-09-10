# GeoShield Backend

FastAPI backend for GeoShield, an explainable IP-intelligence security dashboard.

## Requirements

- Python 3.12+

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows Command Prompt: .venv\Scripts\activate.bat
python -m pip install -e '.[dev]'
cp ../.env.example .env
```

The IP2Location.io API supports keyless requests with a limited daily quota. For higher limits, set `IP2LOCATION_API_KEY` in `.env`.

## Run

```bash
cd backend
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` for the GeoShield dashboard. Generated API documentation is at `http://127.0.0.1:8000/docs`.

## Tests

```bash
cd backend
python -m pytest -q
```

## Quick Demo

With the server running:

```bash
curl -X POST http://127.0.0.1:8000/api/demo/start
curl http://127.0.0.1:8000/api/overview
curl http://127.0.0.1:8000/api/alerts
```

`/api/demo/start` creates deterministic synthetic traffic, including normal requests, a proxy/VPN failed-login sequence, and sensitive-path scanning. Every generated event is marked `synthetic=true`, and all demo profiles use RFC documentation-only IP ranges so they cannot pollute real public-IP lookups.

Click any alert in the dashboard to inspect request details, network intelligence, rule contributions, and the recent same-IP timeline.

## Real Event Ingestion

```bash
curl -X POST http://127.0.0.1:8000/api/events \
  -H 'Content-Type: application/json' \
  -d '{"ip":"8.8.8.8","method":"GET","path":"/","status":200,"synthetic":false}'
```

## Nginx Log Upload

```bash
curl -X POST http://127.0.0.1:8000/api/logs/upload \
  -F 'file=@/path/to/access.log'
```

Malformed lines are skipped and counted. Private, loopback, link-local, reserved, and documentation IP ranges are never sent to the external IP intelligence provider.

## Sample Attack Log

Download `GET /api/demo/sample-log` from the dashboard using **Sample attack log**, then upload it with **Upload Nginx log**. The source fixture is `demo/attack.nginx.log`.
