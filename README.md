# Insight Engine

**Autonomous Financial Forecasting & Anomaly Detection Agent**

A multi-agent system that turns a plain-English question about a stock into a
professional quantitative report — forecasting, anomaly detection, and risk
metrics — with a human checkpoint before anything is distributed externally.

> Kaggle 5-Day AI Agents Capstone — **Agents for Business** track
> Team: Martin & Kasra

---

## What it does

Ask it something like:

> *"Analyze AAPL for the last 6 months. Any anomalies? What's the outlook?"*

and the pipeline will:

1. Ingest OHLCV + macro data (live `yfinance`/FRED, with cached fallback)
2. Forecast 30 days ahead (ARIMA + Prophet ensemble, with confidence bands)
3. Detect statistical anomalies (Z-score + Isolation Forest + Bollinger breach)
4. Compute risk metrics (Sharpe, VaR 95/99, max drawdown, beta, volatility)
5. Critique its own output and loop back if confidence is too low
6. Write a Markdown report with charts
7. **Pause at a human-in-the-loop checkpoint** before any external action
8. Distribute (Drive / Gmail / Calendar / Chat) only after approval

---

## Architecture

```
User question
     │
     ▼
 Orchestrator ──► Data Ingestion ──► ┌ Forecasting ┐
                                     ├ Anomaly     ├──► Critique ──► Report Writer
                                     └ Risk        ┘        │              │
                                                   (loop back if low conf) │
                                                                           ▼
                                                                  ⏸ HITL CHECKPOINT
                                                                           │
                                                                           ▼
                                                                    Distribution
                                                          (Drive · Gmail · Calendar · Chat)
```

Each agent lives in `app/agents/`. The orchestration graph is in
`app/agent.py`. Analytical logic is in `app/core/`. See `specs/insight_engine_spec.md`
for the full spec-driven design and Gherkin scenarios.

---

## Quickstart

This project runs end-to-end **without any cloud credentials** by using the
cached data snapshot and a local report sink. Live data and MCP distribution
activate automatically when credentials are present.

```bash
# 1. Install (Python 3.11+)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the full pipeline locally (cached data, local report only)
python -m app.run --ticker AAPL --months 6

# 3. View the generated report
open artifacts/reports/AAPL_report.md
```

### Optional: live data + distribution

Copy `.env.example` to `.env` and fill in what you have. Anything left blank is
skipped gracefully — the pipeline never hard-fails on a missing credential.

```bash
cp .env.example .env
# edit .env, then:
python -m app.run --ticker AAPL --months 6 --live
```

---

## Course concepts demonstrated

| Concept | Where |
|---|---|
| Multi-agent ADK graph | `app/agent.py`, `app/agents/` |
| MCP servers (Drive/Gmail/Calendar/Chat) | `app/agents/distribution_agent.py`, `app/core/mcp_client.py` |
| Agent Skills (progressive disclosure) | `app/skills/*/SKILL.md` |
| Human-in-the-loop | `app/agents/distribution_agent.py` (`hitl_checkpoint`) |
| Context hygiene / ContextResolver | `app/core/context_resolver.py` |
| Policy server (structural + semantic) | `app/core/policy_server.py` |
| Critique / self-correction loop | `app/agents/critique_agent.py` |
| Evaluation (LLM-as-judge + golden set) | `tests/eval/` |

---

## Notes on stubs

Two things in the spec require infrastructure we keep optional so the project
stays reproducible:

- **MATLAB wavelet decomposition** — implemented in pure Python
  (`scipy`/`PyWavelets`) by default. A MATLAB hook is stubbed behind
  `USE_MATLAB=true` for the thesis extension; it is never required to run.
- **MCP distribution** — `app/core/mcp_client.py` ships a `DryRunMCPClient`
  that logs intended actions. Real MCP calls activate when the relevant
  credentials are set. No keys are ever committed.

---

## Thesis extension hooks

Architected but not implemented in v1 (see spec §"Thesis Extension Points"):
multi-asset correlation, HMM regime detection, a backtesting framework,
GARCH volatility modeling, and news-sentiment correlation.

---

## License

Code: MIT (see `LICENSE`). If this wins the capstone it is additionally
released under CC-BY 4.0 per competition rules.
