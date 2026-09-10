def test_dashboard_root_serves_geoshield_ui(client):
    response=client.get("/")
    assert response.status_code == 200
    assert "GeoShield" in response.text
    assert "Run Demo" in response.text
    assert "Threat activity" in response.text

def test_dashboard_assets_are_served(client):
    js=client.get("/static/dashboard.js")
    css=client.get("/static/dashboard.css")
    assert js.status_code == 200
    assert css.status_code == 200
    assert "/api/overview" in js.text
    assert "/api/alerts" in js.text
    assert "/api/geo/activity" in js.text
    assert "/api/demo/start" in js.text

def test_dashboard_exposes_incident_details_ui(client):
    html=client.get("/").text
    js=client.get("/static/dashboard.js").text
    assert "incidentDrawer" in html
    assert "incidentTimeline" in html
    assert "loadIncident" in js
    assert "/api/alerts/" in js

def test_dashboard_links_to_sample_attack_log(client):
    html=client.get("/").text
    assert "Sample attack log" in html
    assert "/api/demo/sample-log" in html

def test_dashboard_explains_security_pipeline(client):
    html=client.get("/").text
    assert "How GeoShield works" in html
    assert "Ingest" in html
    assert "Enrich" in html
    assert "Score" in html
    assert "Explain" in html
    assert "IP2Location.io" in html
