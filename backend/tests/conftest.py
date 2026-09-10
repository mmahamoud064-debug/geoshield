from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_session
from app.main import create_app
from app.services.ip_intelligence import IPIntelResult


class FakeProvider:
    def lookup(self, ip: str) -> IPIntelResult:
        profiles = {
            "8.8.8.8": IPIntelResult(ip=ip,country_code="US",country_name="United States of America",region="California",city="Mountain View",latitude=37.38605,longitude=-122.08385,asn="15169",isp="Google LLC",is_proxy=True,proxy_type="VPN",raw_data={"fixture":"google-vpn"}),
            "1.1.1.1": IPIntelResult(ip=ip,country_code="AU",country_name="Australia",region="Queensland",city="South Brisbane",latitude=-27.47,longitude=153.02,asn="13335",isp="Cloudflare",is_proxy=False,raw_data={"fixture":"cloudflare"}),
            "9.9.9.9": IPIntelResult(ip=ip,country_code="DE",country_name="Germany",region="Hesse",city="Frankfurt",latitude=50.1109,longitude=8.6821,asn="19281",isp="Quad9",is_proxy=False,raw_data={"fixture":"quad9"}),
        }
        return profiles.get(ip, IPIntelResult(ip=ip, country_code="DE", country_name="Germany", asn="64500"))


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine("sqlite+pysqlite:///:memory:",connect_args={"check_same_thread": False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_session() -> Iterator[Session]:
        with TestSession() as session:
            yield session

    app = create_app()
    app.state.ip_provider = FakeProvider()
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as test_client:
        yield test_client
