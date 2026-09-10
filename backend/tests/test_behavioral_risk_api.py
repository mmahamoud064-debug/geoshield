def test_impossible_travel_alert_uses_previous_user_location(client):
    first = client.post("/api/events", json={"timestamp":"2026-09-07T12:00:00Z","ip":"1.1.1.1","method":"GET","path":"/account","status":200,"user_identifier":"alice","synthetic":False})
    assert first.status_code == 201
    second = client.post("/api/events", json={"timestamp":"2026-09-07T12:10:00Z","ip":"9.9.9.9","method":"GET","path":"/account","status":200,"user_identifier":"alice","synthetic":False})
    assert second.status_code == 201
    assert second.json()["risk_score"] >= 30
    alerts = client.get("/api/alerts").json()
    assert "impossible_travel" in {reason["rule"] for reason in alerts[0]["reasons"]}

def test_new_country_is_flagged_after_stable_recent_baseline(client):
    for minute in range(8):
        response = client.post("/api/events", json={"timestamp":f"2026-09-07T12:{minute:02d}:00Z","ip":"1.1.1.1","method":"GET","path":"/products","status":200,"synthetic":False})
        assert response.status_code == 201
    unusual = client.post("/api/events", json={"timestamp":"2026-09-07T12:08:30Z","ip":"9.9.9.9","method":"GET","path":"/products","status":200,"synthetic":False})
    assert unusual.status_code == 201
    assert unusual.json()["risk_score"] == 10

def test_asn_burst_counts_distinct_source_ips(client):
    ips=["4.2.2.1","4.2.2.2","4.2.2.3","4.2.2.4","4.2.2.5"]
    last=None
    for second,ip in enumerate(ips):
        last=client.post("/api/events", json={"timestamp":f"2026-09-07T13:00:0{second}Z","ip":ip,"method":"GET","path":"/products","status":200,"synthetic":False})
        assert last.status_code == 201
    assert last is not None
    assert last.json()["risk_score"] == 15
