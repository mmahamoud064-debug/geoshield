from datetime import datetime, timezone
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session
from app.core.database import Base
from app.models.entities import Event

def test_models_create_expected_tables_and_persist_event():
    engine=create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    assert set(inspect(engine).get_table_names()) >= {"events","ip_profiles","alerts"}
    with Session(engine) as session:
        event=Event(timestamp=datetime.now(timezone.utc),ip="8.8.8.8",method="GET",path="/",status=200,enrichment_status="pending",synthetic=False,raw_metadata={})
        session.add(event); session.commit()
        assert session.scalar(select(Event).where(Event.ip=="8.8.8.8")) is not None
