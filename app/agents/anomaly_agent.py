"""Anomaly Detection Agent — Z-score + Bollinger + Isolation Forest."""

from __future__ import annotations

from app.core.anomaly_detection import detect


def run(data: dict, cfg=None) -> dict:
    rep = detect(data["dates"], data["close"], data["volume"])
    return {
        "found": rep.found,
        "count": len(rep.anomalies),
        "baseline": rep.baseline,
        "anomalies": [
            {
                "index": a.index,
                "date": a.date,
                "kind": a.kind,
                "severity": a.severity,
                "detail": a.detail,
            }
            for a in rep.anomalies
        ],
    }
