---
name: financial-report-generation
description: >
  Assembles a professional Markdown financial report from forecast, anomaly, and
  risk results. Triggers on "generate report", "write report", "summarize
  findings". Produces a structured template, a price/forecast/anomaly chart, an
  executive summary under 300 words, and a recommendations section. NOT for
  running the underlying analysis — it consumes results those skills produce.
---

# Financial Report Generation

Turn analysis results into a stakeholder-ready report.

## Structure (in order)
1. **Title + provenance** — ticker, data source, day count, forecast confidence.
2. **Executive summary** — < 300 words, plain language, leads with the headline
   forecast and the single most important finding.
3. **Chart** — historical close + forecast + 95% CI band + anomaly markers.
4. **Forecast** — method, horizon, MAPE, endpoint with CI.
5. **Anomaly detection** — table of flagged events, or an honest "none detected"
   with baseline stats.
6. **Risk assessment** — metric table; surface reliability warnings first.
7. **Critique notes** — any confidence caveats from the critique step.
8. **Disclaimer** — model estimates, not investment advice.

## Rules
- Never bury a reliability warning below the metrics it qualifies.
- Always include the disclaimer.
- Keep the executive summary self-contained — a reader who reads only it should
  still get the headline correctly.

## Implementation
See `app/agents/report_agent.py`.
