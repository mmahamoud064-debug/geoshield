from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.database import Base
from app.services.ip_intelligence import IPIntelResult, enrich_ip, is_external_lookup_allowed

class FakeProvider:
    def __init__(self): self.calls=[]
    def lookup(self,ip:str)->IPIntelResult:
        self.calls.append(ip)
        return IPIntelResult(ip=ip,country_code="US",country_name="United States of America",region="California",city="Mountain View",latitude=37.38605,longitude=-122.08385,asn="15169",isp="Google LLC",is_proxy=False,proxy_type=None,raw_data={"fixture":True})

def test_private_and_reserved_ips_are_not_external_lookup_candidates():
    blocked=["127.0.0.1","10.0.0.7","192.168.1.2","::1","169.254.1.1","203.0.113.10"]
    assert all(not is_external_lookup_allowed(ip) for ip in blocked)

def test_public_ip_is_external_lookup_candidate():
    assert is_external_lookup_allowed("8.8.8.8")

def test_enrich_ip_caches_public_lookup():
    engine=create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    provider=FakeProvider()
    with Session(engine) as session:
        first=enrich_ip(session,"8.8.8.8",provider)
        second=enrich_ip(session,"8.8.8.8",provider)
        assert first.id == second.id
        assert first.country_code == "US"
        assert provider.calls == ["8.8.8.8"]

def test_enrich_ip_never_calls_provider_for_private_ip():
    engine=create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    provider=FakeProvider()
    with Session(engine) as session:
        profile=enrich_ip(session,"10.1.2.3",provider)
        assert profile.source == "local"
        assert provider.calls == []
