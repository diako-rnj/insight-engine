---
name: anomaly-detection
description: >
  Statistical anomaly flagging for financial time series. Triggers on
  "anomalies", "unusual activity", "flag", "spike", "outlier". Runs volume
  Z-score analysis, Bollinger Band breach detection, and Isolation Forest, then
  classifies severity and validates significance. NOT for forecasting or risk
  metrics. Must NOT fabricate anomalies when none exceed threshold.
---

# Anomaly Detection

Detect and classify statistically significant events; report honestly when none
exist.

## Procedure
1. **Volume Z-score** — compute against a 20-day rolling mean. Volume > 3σ →
   HIGH significance flag with date, volume delta, and coinciding price move.
2. **Bollinger breach** — flag a close crossing the 2σ band; classify severity
   by sigma distance (2.0–2.5 LOW, 2.5–3.0 MEDIUM, ≥3.0 HIGH).
3. **Isolation Forest** — multivariate (return × volume) cross-check when
   scikit-learn is available; ~2% contamination.
4. **No-anomaly path** — if nothing exceeds threshold, state
   "No statistically significant anomalies detected" and report baseline stats
   (mean, std, thresholds). Do **not** invent anomalies to fill the section.

## Output contract
`found` (bool), `count`, ordered `anomalies` (each with date, kind, severity,
detail), and a `baseline` stats block.

## Implementation
See `app/core/anomaly_detection.py`.
