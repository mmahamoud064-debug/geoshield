from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.alerts import router as alerts_router
from app.api.demo import router as demo_router
from app.api.events import router as events_router
from app.api.geo import router as geo_router
from app.core.database import Base, engine
from app.services.ip_intelligence import IP2LocationHTTPProvider


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="GeoShield", version="0.1.0", lifespan=lifespan)
    web_dir = Path(__file__).resolve().parent / "web"
    app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")

    @app.get("/", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(web_dir / "index.html")
    app.state.ip_provider = IP2LocationHTTPProvider()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(events_router)
    app.include_router(demo_router)
    app.include_router(geo_router)
    app.include_router(alerts_router)
    return app


app = create_app()
