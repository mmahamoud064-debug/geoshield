def test_alert_detail_includes_network_event_and_timeline(client):
    payloads = [
        {"timestamp":"2026-09-07T12:00:00Z","ip":"8.8.8.8","method":"GET","path":"/","status":200},
        {"timestamp":"2026-09-07T12:00:05Z","ip":"8.8.8.8","method":"POST","path":"/admin/login","status":401},
        {"timestamp":"2026-09-07T12:00:10Z","ip":"8.8.8.8","method":"POST","path":"/admin/login","status":401},
    ]
    for payload in payloads:
        assert client.post("/api/events", json=payload).status_code == 201
    alerts = client.get("/api/alerts").json()
    assert alerts
    detail = client.get(f"/api/alerts/{alerts[0]['id']}").json()
    assert detail["event"]["method"] == "POST"
    assert detail["event"]["path"] == "/admin/login"
    assert detail["network"]["country_code"] == "US"
    assert detail["network"]["asn"] == "15169"
    assert detail["network"]["isp"] == "Google LLC"
    assert detail["network"]["is_proxy"] is True
    assert len(detail["timeline"]) == 3
    assert detail["timeline"][-1]["event_id"] == detail["event_id"]
