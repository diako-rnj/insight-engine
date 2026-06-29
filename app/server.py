"""FastAPI Server for the Insight Engine Dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.agent import auto_reject, run_pipeline
from app.core.config import CONFIG, Config

app = FastAPI(title="Insight Engine API")

# Mount the static directory for CSS and JS
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Expose artifacts so the frontend can serve charts
ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
app.mount("/artifacts", StaticFiles(directory=ARTIFACTS_DIR), name="artifacts")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main interactive dashboard."""
    index_file = STATIC_DIR / "index.html"
    return index_file.read_text()


@app.get("/api/run")
async def api_run_pipeline(ticker: str = "AAPL", months: int = 6):
    """Run the entire agent pipeline and return results as JSON."""
    cfg = Config(use_live_data=True)

    # We use auto_reject for the HITL step so the web UI doesn't hang waiting for terminal input.
    result = run_pipeline(ticker, months, cfg, hitl=auto_reject)

    slim = dict(result)
    slim["forecast"] = {
        k: v for k, v in result["forecast"].items() if k not in ("trend", "residual")
    }

    return slim


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
