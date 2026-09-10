@echo off
setlocal
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
  echo [GeoShield] Creating virtual environment...
  python -m venv .venv || exit /b 1
)

echo [GeoShield] Installing dependencies...
.venv\Scripts\python.exe -m pip install -e ".[dev]" || exit /b 1

if not exist ".env" (
  copy "..\.env.example" ".env" >nul || exit /b 1
)

echo [GeoShield] Starting at http://127.0.0.1:8000/
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
