# IP2Location Programming Contest 2026 — Submission Draft

Use this file when the public repository URL is ready. The official submission form asks for name, email, project title, short description, source-code URL, remarks, and how you heard about the contest.

## Project title

**GeoShield — Explainable IP Threat Intelligence**

## Short description — recommended

GeoShield is an open-source security dashboard that turns web access events and Nginx logs into explainable risk alerts. It enriches public IPs with IP2Location.io geographic/network intelligence, combines that context with behavioral signals such as failed requests, sensitive-path probing, traffic bursts, unusual countries and impossible travel, then shows exactly why each alert fired through rule contributions and an incident timeline. A deterministic offline demo and downloadable attack log make the project easy to evaluate in under a minute.

## Short description — compact alternative

GeoShield enriches web traffic with IP2Location.io and converts geographic, network and behavioral signals into explainable security alerts, a global threat map and incident timelines. It supports JSON events, Nginx log uploads, real IP enrichment and a deterministic offline demo.

## Remarks — recommended

The project is intentionally designed to be judge-friendly: one Python server, SQLite, automated tests, a built-in deterministic demo, a downloadable Nginx attack fixture, Swagger documentation, and no Node/npm requirement. Demo IPs use RFC documentation-only ranges and are isolated from real public-IP enrichment.

## Source-code URL

```text
https://github.com/mmahamoud064-debug/geoshield
```

## Final submission checklist

- [x] Public repository is accessible without login.
- [x] MIT open-source license added.
- [ ] README renders correctly on GitHub, including screenshots and Mermaid diagram.
- [x] Fresh Windows setup succeeds using the README commands.
- [x] `python -m pytest -q` passes from `backend/`.
- [x] Dashboard opens at `http://127.0.0.1:8000/`.
- [x] **Run Demo** works from a clean database.
- [x] An alert opens **Incident Details**.
- [x] **Sample attack log** downloads and re-uploads successfully.
- [ ] Real IP2Location enrichment verified with the final API tier/key.
- [x] No `.env`, API key, database or virtualenv committed.
- [ ] Repository URL pasted into the official submission form.
- [ ] Optional: publish a short post with the project link and contest hashtags.

## Official pages

- Contest: https://contest.ip2location.com/
- Terms: https://contest.ip2location.com/terms-and-conditions
- Submission: https://contest.ip2location.com/submission
