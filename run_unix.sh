#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/backend"

if [ ! -x ".venv/bin/python" ]; then
  echo "[GeoShield] Creating virtual environment..."
  python3 -m venv .venv
fi

echo "[GeoShield] Installing dependencies..."
.venv/bin/python -m pip install -e '.[dev]'

if [ ! -f ".env" ]; then
  cp ../.env.example .env
fi

echo "[GeoShield] Starting at http://127.0.0.1:8000/"
exec .venv/bin/python -m uvicorn app.main:app --reload
