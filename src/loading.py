"""Validate saved telemetry and expose factual output independently of AI reporting."""

import json
from datetime import UTC
from pathlib import Path
from statistics import mean

from src.models import Incident


def load_cloudwatch_snapshot(path: Path):
    data = json.loads(path.read_text())
    incident = Incident.model_validate(data["incident"])
    receipt = data.get("ingestion_metadata") or {}
    if (
        incident.data_source != "live CloudWatch"
        or receipt.get("source") != "Amazon CloudWatch"
        or not receipt.get("request_id")
        or not receipt.get("instance_id")
        or receipt.get("samples") != len(incident.metrics)
        or not incident.metrics
    ):
        raise ValueError("This file does not contain a complete recorded CloudWatch collection.")
    return incident, {**receipt, "read_mode": "recorded_snapshot"}


def cpu_overview(incident: Incident):
    samples = sorted(
        (m for m in incident.metrics if m.name == "cpu_percent"), key=lambda m: m.timestamp
    )
    if not samples:
        return None
    return {
        "samples": len(samples),
        "average": mean(m.value for m in samples),
        "peak": max(m.value for m in samples),
        "latest": samples[-1].value,
        "first_at": samples[0].timestamp.astimezone(UTC),
        "last_at": samples[-1].timestamp.astimezone(UTC),
        "above_demo_limit": sum(m.value > 90 for m in samples),
        # Explicit UTC strings prevent the browser from relabeling local time as UTC.
        "rows": [
            {
                "Time (UTC)": m.timestamp.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "CPU (%)": m.value,
            }
            for m in samples
        ],
    }
