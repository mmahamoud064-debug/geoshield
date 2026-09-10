# GeoShield 60-Second Demo Script

This is the recommended flow for a contest judge or short recorded demo.

## 0–10 seconds — establish the problem

> “GeoShield turns web traffic into explainable IP threat intelligence. Instead of only showing where an IP is located, it combines IP2Location context with behavior and tells you exactly why an event is risky.”

Show the dashboard landing state and the four-step flow: **Ingest → Enrich → Score → Explain**.

## 10–25 seconds — run the deterministic demo

Click **Run Demo**.

Point out:

- total and risky-event counters,
- activity appearing on the world map,
- synthetic badges that make demo data explicit,
- alerts appearing with a numeric risk score.

## 25–40 seconds — explain one alert

Click the highest-risk alert.

Point out:

- the source IP and geographic/network context,
- the exact rule contributions such as proxy, failed responses or sensitive path,
- the recent same-IP timeline.

Key line:

> “The analyst never receives a mystery score — every point is explained.”

## 40–52 seconds — prove real log ingestion

Click **Sample attack log**, then **Upload Nginx log** and upload the downloaded file.

Explain that GeoShield parses Nginx combined logs and sends normalized events through the same enrichment and scoring pipeline as the API.

## 52–60 seconds — close on IP2Location

> “For public IPs, GeoShield uses IP2Location.io as the intelligence layer for geographic and network context. The offline demo is isolated using documentation-only IPs, so a judge can always run it even without API quota.”

Optionally open `/docs` and show `POST /api/events` for the full API surface.
