def test_ingestion_pipeline_creates_explainable_high_risk_alert(client):
    payload={"ip":"8.8.8.8","method":"POST","path":"/admin/login","status":401,"synthetic":False}
    for _ in range(3):
        response=client.post("/api/events",json=payload)
        assert response.status_code == 201
    alerts=client.get("/api/alerts").json()
    assert alerts[0]["score"] >= 70
    assert alerts[0]["severity"] == "high"
    assert {reason["rule"] for reason in alerts[0]["reasons"]} >= {"proxy","sensitive_path","failed_responses"}

def test_overview_reports_ingested_events_and_unique_ips(client):
    response=client.post("/api/events",json={"ip":"1.1.1.1","method":"GET","path":"/","status":200,"synthetic":False})
    assert response.status_code == 201
    overview=client.get("/api/overview").json()
    assert overview["total_events"] == 1
    assert overview["unique_ips"] == 1
