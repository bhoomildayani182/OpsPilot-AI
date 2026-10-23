import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.loading import cpu_overview, load_cloudwatch_snapshot
from src.models import Incident
from src.presentation import collection_label


def test_recorded_cloudwatch_snapshot_retains_original_timestamp_and_labels():
    p = Path(__file__).resolve().parents[1] / "artifacts/video/live-investigation.json"
    original = json.loads(p.read_text())
    incident, receipt = load_cloudwatch_snapshot(p)
    assert incident.data_source == "live CloudWatch"
    assert receipt["fetched_at_utc"] == original["ingestion_metadata"]["fetched_at_utc"]
    assert receipt["read_mode"] == "recorded_snapshot"
    assert "Recorded" in collection_label(incident.data_source, receipt)


def test_incomplete_or_synthetic_record_cannot_be_relabelled_as_real(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(
        json.dumps(
            {
                "incident": {
                    "title": "Example incident",
                    "started_at": datetime.now(UTC).isoformat(),
                    "data_source": "synthetic sample",
                },
                "ingestion_metadata": {"source": "Amazon CloudWatch"},
            }
        )
    )
    with pytest.raises(ValueError, match="complete recorded"):
        load_cloudwatch_snapshot(p)


def test_overview_is_exact_observed_cpu_data_not_ai_or_zero_filled():
    incident = Incident(
        title="CPU test incident",
        started_at=datetime.now(UTC),
        metrics=[
            {"name": "cpu_percent", "value": 80.0, "timestamp": "2026-10-22T09:00:00Z"},
            {"name": "cpu_percent", "value": 100.0, "timestamp": "2026-10-22T09:10:00Z"},
        ],
    )
    summary = cpu_overview(incident)
    assert summary["samples"] == 2 and summary["average"] == 90
    assert summary["latest"] == 100 and summary["above_demo_limit"] == 1
    assert len(summary["rows"]) == 2
    assert summary["rows"][0]["Time (UTC)"] == "2026-10-22 09:00:00 UTC"
