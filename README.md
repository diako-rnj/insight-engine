# 📈 Insight Engine

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Track](https://img.shields.io/badge/Track-Agents_for_Business-orange)

## 💡 About
**Autonomous Financial Forecasting & Anomaly Detection Web Dashboard**

Insight Engine is a multi-agent AI system that translates plain-English parameters about a stock into a professional quantitative report. It features an interactive, classy web dashboard where users can query any stock ticker, and the system handles live data ingestion, mathematical forecasting, anomaly detection, and risk metrics. 

It generates an accurate candlestick chart and drafts a fully formatted executive report. Users can click "Read More" to expand a comprehensive analytical methodology deep-dive, or download a professional, legally-sound PDF report directly from the interface.

> **Kaggle 5-Day AI Agents Capstone** — **Agents for Business** track  
> **Team:** CRM

---

## ✨ What It Does

Provide a simple input in the web interface:
> *"Analyze AAPL for the last 6 months."*

The agent pipeline automatically:
1. **Ingests Live Data:** Pulls live OHLCV + macro data strictly using `yfinance`.
2. **Forecasts:** Projects 30 days ahead using an ARIMA + Prophet ensemble, complete with confidence bands.
3. **Detects Anomalies:** Identifies statistical anomalies via Z-score, Isolation Forest, and Bollinger band breaches.
4. **Evaluates Risk:** Computes critical risk metrics including Sharpe ratio, VaR (95/99), max drawdown, beta, and volatility.
5. **Generates Reports:** Drafts a massive, 2-page deep-dive AI Synthesis report covering methodology, market microstructure, and macroeconomics.
6. **Visualizes Results:** Renders a gorgeous, highly interactive Candlestick chart overlaid with the forecast using `TradingView Lightweight Charts`.
7. **Ultra-Compact UI:** Features an intelligent CSS Grid layout designed to fit critical data on a single screen while offering a smooth scrolling mechanism for deep-dive texts.
8. **Professional Exports:** Includes a robust PDF generator that outputs a branded, highly-aesthetic, formatted document, as well as a pure Markdown option.

---

## 🏗 Architecture

```text
User Request (Web Dashboard)
      │
      ▼
 Orchestrator ──► Data Ingestion (yfinance) ──► ┌ Forecasting ┐
                                                ├ Anomaly     ├──► Critique ──► Report Writer
                                                └ Risk        ┘                     │
                                                                                    ▼
                                                                     Interactive, Compact Web UI
                                                             (Lightweight Charts & Professional PDF Export)
```

Each agent lives in `app/agents/`. The orchestration graph is defined in `app/agent.py`, the web interface is served via FastAPI in `app/server.py`, and the quantitative analytical logic is isolated in `app/core/`.

---

## 🚀 Quickstart

Insight Engine is designed to be highly reproducible and runs entirely locally.

### 1. Setup the Environment

```bash
# 1. Clone the repository
git clone https://github.com/diako-rnj/insight-engine.git
cd insight-engine

# 2. Setup the environment (Python 3.11+)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Dashboard

The project ships with a FastAPI-powered Web UI.

```bash
uvicorn app.server:app --reload
```

Then, open your browser and navigate to:
**http://127.0.0.1:8000**

You'll be greeted by an interactive, matte-dark dashboard featuring smooth macOS-style loading indicators. Type in a ticker (e.g. `AAPL`), select your timeframe, and let the agents do the rest! 

Once the analysis is complete, you can click **•••** to expand the deep-dive methodology, or click **Download PDF** to seamlessly export a professional, white-background, black-text report straight from your browser.

---

## 📂 Project Structure

```text
insight_engine/
├── app/
│   ├── agents/          # Agent implementations (Forecasting, Anomaly, Risk, etc.)
│   ├── core/            # Quantitative analysis, Data Ingestion
│   ├── static/          # Web dashboard assets (HTML, JS, CSS)
│   ├── server.py        # FastAPI server entrypoint
│   └── run.py           # CLI entrypoint
├── artifacts/           # Outputs: Generated charts and markdown reports
├── specs/               # Product spec and Gherkin scenarios (The source of truth)
├── AGENTS.md            # Agent behavioral rules and context
├── README.md            # Project documentation
└── requirements.txt     # Python dependencies
```

---

## 📝 License

This project's code is licensed under the **MIT License** (see `LICENSE`). If selected as a winning capstone submission, it will additionally be released under **CC-BY 4.0** as per the competition rules.
