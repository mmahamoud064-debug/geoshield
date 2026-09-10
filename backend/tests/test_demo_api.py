def test_demo_start_generates_synthetic_alerts(client):
    response=client.post("/api/demo/start")
    assert response.status_code == 200
    payload=response.json()
    assert payload["synthetic_events"] >= 8
    assert payload["alerts_created"] >= 2
    overview=client.get("/api/overview").json()
    assert overview["total_events"] == payload["synthetic_events"]
    assert overview["active_alerts"] == payload["alerts_created"]

def test_demo_does_not_require_external_ip_provider(client):
    class ExplodingProvider:
        def lookup(self, ip:str):
            raise AssertionError(f"demo unexpectedly called external provider for {ip}")
    client.app.state.ip_provider=ExplodingProvider()
    response=client.post("/api/demo/start")
    assert response.status_code == 200
    assert response.json()["synthetic_events"] >= 8

def test_demo_profiles_never_shadow_real_public_ip_lookup(client):
    from app.services.ip_intelligence import IPIntelResult
    class RecordingProvider:
        def __init__(self): self.calls=[]
        def lookup(self, ip:str)->IPIntelResult:
            self.calls.append(ip)
            return IPIntelResult(ip=ip,country_code="US",country_name="United States",city="Mountain View",asn="15169",isp="Google LLC",is_proxy=False,raw_data={"fixture":"real-public-lookup"})
    provider=RecordingProvider()
    client.app.state.ip_provider=provider
    assert client.post("/api/demo/start").status_code == 200
    response=client.post("/api/events",json={"ip":"8.8.8.8","method":"GET","path":"/","status":200,"synthetic":False})
    assert response.status_code == 201
    assert response.json()["is_proxy"] is False
    assert provider.calls == ["8.8.8.8"]

def test_demo_uses_only_non_public_documentation_addresses():
    from app.services.demo import build_demo_events
    from app.services.ip_intelligence import is_external_lookup_allowed
    ips={event.ip for event in build_demo_events()}
    assert ips
    assert all(not is_external_lookup_allowed(ip) for ip in ips)

def test_sample_attack_log_is_downloadable(client):
    response=client.get("/api/demo/sample-log")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition","").lower()
    assert "/admin/login" in response.text
