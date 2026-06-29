# Insight Engine — Capstone Submission Guide

**Team:** Martin & Kasra
**Track:** Agents for Business
**Deadline:** July 6, 2026 · 11:59 PM PT
**Project:** Insight Engine — Autonomous Financial Forecasting & Anomaly Detection Agent

This guide answers two things: (1) exactly what to upload and where, and
(2) the full video transcript to read aloud while recording.

---

## Part 1 — What to upload, and where

A valid submission is **one Kaggle Writeup** with four required pieces attached.
Here is each piece, the destination, and what goes in it.

### 1. GitHub repository (the code)

**Where:** push the `insight_engine/` folder (from `insight_engine.zip`) to a
**public** GitHub repo.

**Steps:**
```bash
unzip insight_engine.zip
cd insight_engine
git init
git add .
git commit -m "Insight Engine — multi-agent financial analysis pipeline"
git branch -M main
git remote add origin https://github.com/<your-username>/insight-engine.git
git push -u origin main
```

**Checklist before pushing:**
- [ ] `.env` is NOT committed (`.gitignore` already excludes it — confirm `git status` doesn't list it)
- [ ] `README.md` is present at the repo root (it has the reproducible setup steps the rules require)
- [ ] Repo visibility is set to **Public**
- [ ] `LICENSE` (MIT) is present

> Why this matters: the rules require a public codebase with detailed setup
> instructions, AND winners' code must be able to regenerate the submission.
> The README covers both. No keys are anywhere in the code.

### 2. Live project link (the demo)

**Where:** the "Public Project Link" field on the Writeup.

**Two options — pick one:**

- **Option A (simplest, satisfies the rule):** use the **GitHub repo URL** as the
  project link. The rules explicitly allow a public code repo with setup
  instructions when a live demo isn't feasible.
- **Option B (stronger "wow"):** deploy to **Agent Runtime** + a small **Cloud Run**
  frontend (needs your Google Cloud project with billing). If you do this, the
  project link is the live Cloud Run URL. This is the Day 5 deployment pattern.

> Recommendation given the timeline: ship **Option A** first so you have a valid
> submission locked in. Upgrade to Option B only if time allows before July 6.

### 3. Video (the pitch)

**Where:** upload to **YouTube** (public or unlisted-but-accessible), then attach
the YouTube link to the Writeup's **Media Gallery**.

**Hard limits:** 5 minutes or less. Must be published to YouTube. Required.

**What to record:** screen recording of a terminal + the generated report, with
voiceover. Full transcript is in Part 2 below.

### 4. Cover image (required to submit)

**Where:** Media Gallery. A cover image is mandatory or the Writeup won't submit.

**Easiest source:** the generated chart PNG. After a run, grab
`artifacts/charts/AAPL_chart.png` — it shows the price line, forecast band, and
red anomaly markers. That single image communicates the whole project visually.

### 5. The Writeup text itself

**Where:** the Kaggle Writeup body. **2,500 words max** (penalty if over).
Select the **Agents for Business** track in the Writeup before submitting.

> Note: if you attach a private Kaggle resource to a public Writeup, it becomes
> public after the deadline. Keep everything public from the start to avoid surprises.

### Submission order (do this on July 6, well before 11:59 PM PT)

1. Push repo to GitHub (public)
2. Record + upload video to YouTube
3. Create New Writeup → select **Agents for Business** track
4. Paste Writeup text · attach cover image · attach YouTube video · paste project link
5. Save, then click **Submit** (top-right). A saved draft is NOT a submission.

---

## Part 2 — Video transcript (read aloud)

Target: ~4:30 spoken, leaving buffer under the 5-minute cap. Sections are timed.
Stage directions are in [brackets] — don't read those.

---

### [0:00–0:35] — The problem

> "Financial analysts spend most of their day on repetitive work — pulling data,
> running models, formatting reports — and very little of it on actual judgment.
> We built Insight Engine to flip that ratio.
>
> It's a multi-agent system. You give it a ticker and a plain-English question,
> and it runs the whole quantitative pipeline: it forecasts, it hunts for
> anomalies, it computes risk metrics, it writes a professional report — and
> then it stops, and waits for a human, before anything goes out the door.
>
> Let me show you it running."

[Have the terminal open, repo directory visible.]

---

### [0:35–1:30] — Live run

> "I'll ask it to analyze Apple over the last six months."

[Type and run:]
```bash
python -m app.run --ticker AAPL --months 6
```

> "Watch the trace line. You can see the pipeline move through its stages:
> it ingests the data, then three agents run in parallel — forecasting, anomaly
> detection, and risk. A critique agent reviews the quality. Then the report gets
> written. And right here — it pauses. This is the human-in-the-loop checkpoint.
>
> It's showing me exactly what it wants to send externally: the summary, the
> email recipient, the Drive destination, the calendar event. Nothing has left
> yet. I'm in control. For now, I'll reject it."

[Type `n` at the prompt.]

> "And notice — distribution status is 'rejected.' Zero external actions taken.
> The report is saved locally only. That's the safety contract working."

---

### [1:30–2:30] — The architecture

[Switch to showing the architecture diagram in the spec or README.]

> "Under the hood this is seven agents wired into a graph, built on the ADK
> pattern from the course. An orchestrator routes the request. A data ingestion
> agent pulls live market data, with a cached snapshot as a fallback so the
> system never hard-fails. Then forecasting, anomaly detection, and risk run.
>
> The forecasting agent ensembles two models — ARIMA and Prophet — and always
> reports its confidence as a MAPE score. If confidence is too low, the critique
> agent loops it back to widen the bands. It won't quietly hand you a shaky number.
>
> The anomaly agent uses volume Z-scores, Bollinger band breaches, and an
> Isolation Forest. And critically — when it finds nothing, it says so. It does
> not fabricate anomalies to fill the section.
>
> The risk agent computes Sharpe, Value-at-Risk, max drawdown, beta, and
> volatility — and flags when there isn't enough history to trust them."

---

### [2:30–3:30] — Security (the differentiator)

> "Here's what I think sets this apart. Security isn't bolted on — it's the
> architecture.
>
> First, the human checkpoint you already saw — nothing external happens without
> explicit approval.
>
> Second, a two-layer policy server. Let me show you. I'll approve a run as an
> 'analyst' role."

[Run, showing the distribution output with the gmail block:]
```bash
GMAIL_RECIPIENT="team@example.com" DRIVE_FOLDER="/Reports" \
  python -m app.run --ticker MSFT --months 6 --yes --json
```

> "Look at the distribution results. Drive, calendar, and chat went through as
> dry-run actions. But the email — blocked. The policy server stopped it,
> because the analyst role isn't permitted to send email. That's a deterministic
> rule, not a suggestion to the model.
>
> Third, context hygiene. Sensitive values never live in the agent's context as
> raw text — they're placeholders, resolved at the last second, and any PII in
> outbound text is scrubbed. This directly prevents the kind of accident where an
> agent emails the wrong people real data."

---

### [3:30–4:10] — The output + evaluation

[Open `artifacts/reports/AAPL_report.md` in a viewer, scroll through it.]

> "The result is this — a clean Markdown report. Executive summary up top, the
> chart with forecast bands and red anomaly markers, the forecast detail, the
> anomaly table, and the risk metrics. This is what an analyst would actually
> hand to a stakeholder.
>
> And we didn't just build it — we proved it works. Fourteen tests pass, covering
> the forecasting, anomaly, and risk logic, plus the security scenarios. And a
> five-case golden evaluation set scores it on routing correctness and security
> containment — five out of five."

[Optionally show:]
```bash
python -m pytest -q && python -m tests.eval.grade
```

---

### [4:10–4:30] — Close

> "Insight Engine shows that a multi-agent system can own the entire quantitative
> pipeline — forecasting, anomaly detection, risk, and reporting — while keeping
> a human firmly in control of anything that leaves the building. It's
> reproducible, it's secure by design, and the whole thing is open source.
>
> Thanks for watching."

---

## Recording tips

- **Tool:** any screen recorder (OBS is free; QuickTime on Mac; Xbox Game Bar on
  Windows). Record at 1080p if you can.
- **Do a dry run first** so the terminal output you film is clean and the anomaly
  count looks sensible (~10–12, not dozens).
- **Pre-generate the report** before filming the report walkthrough, so you're not
  waiting on screen.
- **Keep your face/voice optional** — a clear voiceover over the screen recording
  is enough. Energy in the voice matters more than being on camera.
- **Captions help** judges who skim — YouTube auto-captions are fine; correct the
  product name "Insight Engine" if it mis-hears it.

## Final pre-submit checklist

- [ ] GitHub repo public, README present, no `.env` committed
- [ ] Video ≤ 5 min, uploaded to YouTube, link works in incognito
- [ ] Cover image attached (the chart PNG works)
- [ ] Project link added (repo URL, or live Cloud Run URL)
- [ ] Writeup ≤ 2,500 words, **Agents for Business** track selected
- [ ] Clicked **Submit** — confirmed it's no longer a draft
