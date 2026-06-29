---
name: time-series-analysis
description: >
  Forecasting workflow for financial price series. Triggers on "analyze [ticker]",
  "forecast", "price prediction", "time series", "outlook". Runs stationarity
  testing, ARIMA grid search, Prophet fit, ensemble combination, and confidence
  interval generation. NOT for anomaly flagging (use anomaly-detection) or risk
  metrics (use risk assessment).
---

# Time-Series Analysis

Systematic forecasting for a single financial instrument.

## Procedure
1. **EDA & stationarity** — plot the series; run an ADF test. If non-stationary,
   difference once and re-test before model selection.
2. **ARIMA** — fit `ARIMA(p,d,q)`; default `(2,1,2)`. Prefer a small grid search
   over AIC when compute allows.
3. **Prophet** — fit trend + seasonality when ≥ 2 seasonal cycles are present.
4. **Ensemble** — average point forecasts; keep the wider band of the two.
5. **Confidence** — backtest MAPE on a hold-out tail. Report it. If MAPE exceeds
   the configured threshold, hand control to the critique step to widen bands.

## Output contract
A forecast object with `point`, `lower`, `upper`, `mape`, `method`, and a
trend/seasonality/residual decomposition. Never present a point forecast without
its confidence band and MAPE.

## Implementation
See `app/core/forecasting.py`. The skill degrades to a documented drift baseline
when `statsmodels`/`prophet` are unavailable so the pipeline always returns a
forecast.
