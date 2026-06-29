# 📈 Insight Engine

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Track](https://img.shields.io/badge/Track-Agents_for_Business-orange)

**Autonomous Financial Forecasting & Anomaly Detection Agent**

Insight Engine is a multi-agent system that translates plain-English questions about a stock into a professional quantitative report. It handles forecasting, anomaly detection, and risk metrics, while firmly keeping a human-in-the-loop (HITL) before any data is distributed externally.

> **Kaggle 5-Day AI Agents Capstone** — **Agents for Business** track  
> **Team:** Martin & Kasra

---

## ✨ What It Does

Provide a simple prompt:
> *"Analyze AAPL for the last 6 months. Any anomalies? What's the outlook?"*

The pipeline automatically:
1. **Ingests Data:** Pulls OHLCV + macro data (live `yfinance`/FRED, with a cached fallback for robustness).
2. **Forecasts:** Projects 30 days ahead using an ARIMA + Prophet ensemble, complete with confidence bands.
3. **Detects Anomalies:** Identifies statistical anomalies via Z-score, Isolation Forest, and Bollinger band breaches.
4. **Evaluates Risk:** Computes critical risk metrics including Sharpe ratio, VaR (95/99), max drawdown, beta, and volatility.
5. **Self-Critiques:** Reviews its own output and loops back if confidence scores are too low.
6. **Generates Reports:** Drafts a clean Markdown report with embedded charts.
7. **Human-in-the-Loop:** ⏸ **Pauses at a HITL checkpoint** before executing any external action.
8. **Distributes:** Safely shares the report (Drive, Gmail, Calendar, Chat) **only** after explicit approval.

---

## 🏗 Architecture

```text
User Question
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

Each agent lives in `app/agents/`. The orchestration graph is defined in `app/agent.py`, while the quantitative analytical logic is isolated in `app/core/`. For a comprehensive view of the spec-driven design, check out `specs/insight_engine_spec.md`.

---

## 🚀 Quickstart

Insight Engine is designed to be highly reproducible. It runs end-to-end **without any cloud credentials** out-of-the-box by leveraging cached data snapshots and generating local reports.

### 1. Local Run (No Credentials Required)

```bash
# 1. Clone the repository
git clone https://github.com/diako-rnj/insight-engine.git
cd insight-engine

# 2. Setup the environment (Python 3.11+)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Run the pipeline locally (Uses cached data, local report only)
python -m app.run --ticker AAPL --months 6

# 4. View the generated report
open artifacts/reports/AAPL_report.md
```

### 2. Live Run (Optional: Live Data + Distribution)

Want live data and external distribution? Copy `.env.example` to `.env` and fill in the available credentials. Missing credentials will fail gracefully, meaning the pipeline never hard-crashes if a key is missing.

```bash
cp .env.example .env
# Edit .env with your keys, then run:
python -m app.run --ticker AAPL --months 6 --live
```

---

## 📂 Project Structure

```text
insight_engine/
├── app/
│   ├── agents/          # Agent implementations (Forecasting, Anomaly, Risk, etc.)
│   ├── core/            # Quantitative analysis, Data Ingestion, Policy Server
│   ├── skills/          # Skill definitions for specific analytical domains
│   └── run.py           # Application entrypoint
├── artifacts/           # Outputs: Generated charts and markdown reports
├── specs/               # Product spec and Gherkin scenarios (The source of truth)
├── tests/               # Test suites (Unit testing & Eval grading)
├── AGENTS.md            # Agent behavioral rules and context
├── README.md            # Project documentation
└── requirements.txt     # Python dependencies
```

---

## 🧠 Course Concepts Demonstrated

| Concept | Implementation Location |
|---------|-------------------------|
| **Multi-agent ADK graph** | `app/agent.py`, `app/agents/` |
| **MCP servers** *(Drive/Gmail/Calendar/Chat)* | `app/agents/distribution_agent.py`, `app/core/mcp_client.py` |
| **Agent Skills** *(Progressive disclosure)* | `app/skills/*/SKILL.md` |
| **Human-in-the-Loop (HITL)** | `app/agents/distribution_agent.py` (`hitl_checkpoint`) |
| **Context Hygiene / ContextResolver** | `app/core/context_resolver.py` |
| **Policy Server** *(Structural & Semantic)* | `app/core/policy_server.py` |
| **Critique / Self-Correction Loop** | `app/agents/critique_agent.py` |
| **Evaluation** *(LLM-as-judge + golden set)* | `tests/eval/` |

---

## 🛡 Notes on Stubs & Security

To ensure this project remains perfectly reproducible for judging and usage:
- **MATLAB Wavelet Decomposition:** Implemented in pure Python (`scipy`/`PyWavelets`) by default. A MATLAB hook is stubbed behind `USE_MATLAB=true` as an extension, but never required.
- **MCP Distribution:** We ship a `DryRunMCPClient` in `app/core/mcp_client.py` that safely logs intended actions. Actual network calls only trigger when valid credentials are set.
- **Context Hygiene:** Sensitive PII and API keys never reside in the agent's context as raw text; they are substituted with placeholders and scrubbed out before external requests.

---

## 📝 License

This project's code is licensed under the **MIT License** (see `LICENSE`). If selected as a winning capstone submission, it will additionally be released under **CC-BY 4.0** as per the competition rules.
