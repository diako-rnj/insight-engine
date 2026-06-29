# Insight Engine — Financial Forecasting & Anomaly Detection Agent
## Spec-Driven Development Document
**Author:** Martin (data analytics student)
**Track:** Agents for Business — Kaggle 5-Day AI Agents Capstone
**Date:** June 2026
**Version:** 1.0

---

## Background (The Why)

Financial analysts spend 70-80% of their time on repetitive data gathering,
model running, and report formatting — leaving little time for actual judgment.
Insight Engine automates the full quantitative analysis pipeline: from a plain
English question to a professional report delivered to stakeholders, with a
human checkpoint before anything goes external.

The agent demonstrates that multi-agent AI systems can handle the computational
and formatting work of quantitative finance, freeing analysts to focus on
interpretation and strategy.

---

## Technical Stack

```yaml
runtime:
  orchestration: Google ADK 2.0
  deployment: Agent Runtime (Google Cloud) + Cloud Run frontend
  language: Python 3.11+

data_sources:
  primary: yfinance==0.2.40        # live OHLCV + fundamentals
  macro: fredapi==0.5.2            # Federal Reserve economic data
  fallback: static CSV (S&P 500 components)

analysis:
  forecasting:
    - statsmodels==0.14.2          # ARIMA, SARIMA
    - prophet==1.1.5               # Meta Prophet (trend + seasonality)
  anomaly_detection:
    - scikit-learn==1.4.2          # Isolation Forest
    - scipy==1.13.0                # Z-score, statistical tests
  risk_metrics:
    - numpy==1.26.4
    - pandas==2.2.2
  signal_processing:
    - matlab.engine                # Wavelet decomposition (MATLAB)
  visualization:
    - matplotlib==3.9.0
    - seaborn==0.13.2
    - plotly==5.22.0

storage:
  local: SQLite (analysis history, model results)
  cloud: Google Drive MCP (reports + charts)

mcp_servers:
  - gmail: executive summary distribution
  - drive: full report storage
  - calendar: follow-up scheduling
  - chat: team notification
  - developer_knowledge: API documentation lookup

security:
  hitl: required before all external distribution
  context_hygiene: ContextResolver for all tool args
  policy_server: read-only on market APIs, write on reports only
  sandbox: terminal sandboxing enabled
```

---

## Architecture

```
User: "Analyze AAPL for the last 6 months. Any anomalies? What's the outlook?"
                              ↓
                    ┌─────────────────┐
                    │  Orchestrator   │  (ADK LlmAgent)
                    │     Agent       │  Parses intent, routes pipeline
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Data Ingestion  │  yfinance + FRED API
                    │     Agent       │  OHLCV, volume, macro indicators
                    └────────┬────────┘
                             ↓
           ┌─────────────────┼─────────────────┐
           ↓                 ↓                  ↓
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  Forecasting │  │   Anomaly    │  │     Risk     │
  │    Agent     │  │  Detection   │  │  Assessment  │
  │ ARIMA+Prophet│  │    Agent     │  │    Agent     │
  │ MATLAB wavelet│  │ Z-score+IsoF│  │ Sharpe+VaR  │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         └─────────────────┼──────────────────┘
                           ↓
                  ┌─────────────────┐
                  │   Critique      │  Reviews confidence,
                  │    Agent        │  loops back if quality
                  └────────┬────────┘  insufficient
                           ↓
                  ┌─────────────────┐
                  │  Report Writer  │  Markdown report +
                  │    Agent        │  charts + recommendations
                  └────────┬────────┘
                           ↓
                    ⏸ HITL CHECKPOINT
                    Human reviews before
                    anything goes external
                           ↓
                  ┌─────────────────┐
                  │  Distribution   │
                  │    Agent        │
                  └────────┬────────┘
          ┌────────────────┼────────────────┐────────────────┐
          ↓                ↓                ↓                ↓
    Drive MCP         Gmail MCP       Calendar MCP      Chat MCP
    Full report    Exec summary     Follow-up mtg    Team notif
```

---

## Gherkin Scenarios

### Feature: Financial Time Series Forecasting

```gherkin
Scenario: User requests single stock forecast
  Given the user provides ticker "AAPL" and time horizon "6 months"
  When the Data Ingestion Agent fetches OHLCV data from yfinance
  And the Forecasting Agent runs ARIMA and Prophet models
  Then the agent produces a 30-day price forecast with 95% confidence intervals
  And the forecast includes trend decomposition (trend, seasonality, residual)
  And the Report Writer generates a chart with historical + projected prices

Scenario: Forecast confidence is too low
  Given the Forecasting Agent produces a model with MAPE > 15%
  When the Critique Agent reviews the forecast quality
  Then the Critique Agent flags low confidence
  And loops back to Forecasting Agent with instruction to widen confidence bands
  And the final report clearly states forecast uncertainty level

Scenario: Macro indicator correlation detected
  Given FRED data shows Fed funds rate increased 50bps in the analysis window
  When the Forecasting Agent incorporates macro context
  Then the report includes a section on macro factor sensitivity
  And notes correlation between rate change and price movement
```

### Feature: Anomaly Detection

```gherkin
Scenario: Volume spike anomaly detected
  Given 6 months of OHLCV data for a ticker
  When the Anomaly Detection Agent runs Z-score analysis on daily volume
  And a trading day shows volume > 3 standard deviations above the 20-day mean
  Then the agent flags it as a HIGH significance anomaly
  And the report marks the date on the price chart with a red indicator
  And provides context: date, volume delta, coinciding price movement

Scenario: Price deviation from moving average detected
  Given a ticker's price crosses above its 2-sigma Bollinger Band
  When the Anomaly Detection Agent detects the breach
  Then the agent classifies it as an "overextension signal"
  And records it with severity level (1-3 sigma bands)
  And the Critique Agent validates statistical significance (p < 0.05)

Scenario: No significant anomalies found
  Given analysis produces no events exceeding detection thresholds
  When the Anomaly Detection Agent completes its scan
  Then the report states "No statistically significant anomalies detected"
  And provides the baseline statistics (mean, std, threshold used)
  And does NOT fabricate anomalies to fill the section
```

### Feature: Risk Assessment

```gherkin
Scenario: Standard risk metrics computed
  Given at least 252 trading days of price history (1 year)
  When the Risk Assessment Agent runs metric calculations
  Then the report includes:
    | Metric              | Method                    |
    | Sharpe Ratio        | (return - rf) / std_dev   |
    | VaR 95%             | Historical + Parametric   |
    | VaR 99%             | Historical + Parametric   |
    | Max Drawdown        | Peak-to-trough            |
    | Beta vs S&P 500     | Covariance / market var   |
    | Annualized Volatility| Rolling 30-day            |

Scenario: Insufficient history for reliable metrics
  Given fewer than 60 trading days of price data available
  When the Risk Assessment Agent attempts calculation
  Then the agent flags "Insufficient history — metrics may be unreliable"
  And computes available metrics with explicit confidence warnings
  And does NOT silently produce misleading statistics
```

### Feature: Security & Human-in-the-Loop

```gherkin
Scenario: HITL checkpoint before distribution
  Given the Report Writer Agent has completed a full analysis report
  When the Distribution Agent is ready to send externally
  Then execution PAUSES and presents the human with:
    | Item              | Preview                      |
    | Report summary    | First 200 words              |
    | Gmail recipient   | Target email address         |
    | Drive destination | Target folder path           |
    | Calendar event    | Date, title, attendees       |
  And waits for explicit human approval before proceeding

Scenario: User rejects HITL checkpoint
  Given the human reviews and rejects at the HITL checkpoint
  When the user provides rejection with optional feedback
  Then the Distribution Agent halts all external actions
  And the report is saved locally only
  And the Orchestrator logs the rejection with timestamp

Scenario: Context hygiene — no PII in agent context
  Given the user provides a ticker and optional notes
  When the ContextResolver preprocesses all tool arguments
  Then all [[VARIABLE_NAME]] placeholders are resolved from env vars
  And no hardcoded emails, API keys, or personal data exist in agent context
  And tool arguments are logged post-resolution for audit
```

### Feature: Report Generation & Distribution

```gherkin
Scenario: Full pipeline completes successfully
  Given a valid ticker and sufficient market data
  When the full agent pipeline executes without errors
  Then the Distribution Agent:
    | Action              | Output                                    |
    | Drive MCP           | Saves PDF report + PNG charts to folder   |
    | Gmail MCP           | Sends executive summary (< 300 words)     |
    | Calendar MCP        | Creates follow-up review event (1 week)   |
    | Chat MCP            | Posts "Analysis complete" notification    |
  And all actions are logged to SQLite with timestamp + status

Scenario: Partial failure — one MCP unavailable
  Given the Gmail MCP is temporarily unavailable
  When the Distribution Agent attempts full distribution
  Then Drive, Calendar, and Chat actions complete successfully
  And the failed Gmail action is logged with error details
  And the report notes partial distribution in the audit trail
  And the agent does NOT retry indefinitely (max 3 attempts)
```

---

## Skills

### Skill 1: time-series-analysis
**Trigger:** "analyze [ticker]", "forecast", "price prediction", "time series"
**What it does:** Systematic EDA + stationarity test (ADF) + ARIMA grid search +
Prophet fit + ensemble combination + confidence interval generation

### Skill 2: anomaly-detection
**Trigger:** "anomalies", "unusual activity", "flag", "spike", "outlier"
**What it does:** Z-score computation + Isolation Forest + Bollinger Band breach
detection + significance testing + severity classification

### Skill 3: financial-report-generation
**Trigger:** "generate report", "write report", "summarize findings"
**What it does:** Structured Markdown report template + chart generation +
executive summary extraction + recommendations section

---

## Policy Server Rules

```yaml
environments:
  development:
    blocked_tools:
      - gmail_send
      - calendar_create
  production:
    blocked_tools: []

roles:
  analyst:
    allowed_tools:
      - yfinance_fetch
      - fred_fetch
      - drive_read
      - drive_write
      - run_python
      - run_matlab
  reviewer:
    allowed_tools:
      - "*"
```

---

## Evaluation Metrics

| Metric | Target | Method |
|---|---|---|
| Forecast MAPE | < 10% on test set | Backtesting last 30 days |
| Anomaly precision | > 80% | Manual label validation |
| Pipeline completion | 100% on valid tickers | Integration test |
| HITL trigger rate | 100% before distribution | Hook test |
| Report generation time | < 120 seconds | Timing benchmark |

---

## Thesis Extension Points (Future Work)

The following are deliberately left as extension hooks — not implemented in v1
but architected to be added without rebuilding:

1. **Multi-asset correlation matrix** — extend Data Ingestion to accept
   portfolio of tickers, add cross-asset analysis agent (→ Option C territory)
2. **Regime detection** — add Hidden Markov Model agent to classify bull/bear
   regimes and condition forecasts on regime state
3. **Backtesting framework** — add BacktestAgent that simulates trading signals
   generated by anomaly detection across historical windows
4. **GARCH volatility modeling** — extend Risk Assessment Agent with ARCH/GARCH
   for conditional heteroskedasticity (standard in academic finance papers)
5. **Sentiment integration** — add NewsAgent that fetches financial news and
   scores sentiment to correlate with price anomalies
