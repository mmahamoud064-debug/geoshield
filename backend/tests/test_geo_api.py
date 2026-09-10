def test_geo_activity_aggregates_events_by_enriched_location(client):
    client.post("/api/events", json={"ip":"1.1.1.1","method":"GET","path":"/","status":200,"synthetic":False})
    client.post("/api/events", json={"ip":"8.8.8.8","method":"GET","path":"/","status":200,"synthetic":False})
    response=client.get("/api/geo/activity")
    assert response.status_code == 200
    points={item["country_code"]:item for item in response.json()}
    assert points["AU"]["event_count"] == 1
    assert points["AU"]["latitude"] == -27.47
    assert points["US"]["event_count"] == 1
    assert points["US"]["risky_count"] == 1
