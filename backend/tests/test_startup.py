from fastapi.testclient import TestClient
from sqlalchemy import inspect
from app.core.database import Base, engine
from app.main import create_app

def test_application_startup_initializes_database_schema():
    Base.metadata.drop_all(engine)
    assert "events" not in inspect(engine).get_table_names()
    with TestClient(create_app()):
        pass
    assert set(inspect(engine).get_table_names()) >= {"events","ip_profiles","alerts"}
