import pytest
from pydantic import ValidationError

from src.data.sample_incidents import SAMPLES, get_sample
from src.models import Incident
from src.tools.deployment_analyzer import analyze_deployments
from src.tools.log_analyzer import analyze_logs
from src.tools.metrics_analyzer import analyze_metrics


@pytest.mark.parametrize("name", SAMPLES)
def test_sample_fixtures_have_valid_synthetic_provenance(name):
    incident = get_sample(name)
    assert incident.data_source == "synthetic sample"
    get_sample(name).metrics.clear()
    assert len(get_sample(name).metrics) == len(incident.metrics)


def test_metrics_exact_statistics_and_strict_threshold():
    incident = get_sample("CPU saturation")
    result = analyze_metrics(incident)
    assert result.details["cpu_percent"] == {
        "min": 88,
        "max": 97,
        "mean": 93.75,
        "samples": 4,
        "above_threshold": 3,
        "threshold": 90,
    }
    incident.metrics[0].value = 90
    assert analyze_metrics(incident).details["cpu_percent"]["above_threshold"] == 3
    assert all(e.source == "synthetic sample" for e in result.evidence)


def test_empty_tools_do_not_claim_health():
    incident = Incident(title="Unknown infrastructure issue", started_at="2026-10-22T09:00:00Z")
    for analyzer in (analyze_metrics, analyze_logs, analyze_deployments):
        result = analyzer(incident)
        assert not result.evidence
        assert any("No " in limitation for limitation in result.limitations)


def test_logs_preserve_literal_evidence_and_count_patterns():
    result = analyze_logs(get_sample("Database timeouts"))
    assert result.details["total_lines"] == 2
    assert result.details["patterns"]["timeout"] == 2
    assert "DatabaseTimeoutException" in result.evidence[0].observation
    assert result.evidence[0].id == "L1"


def test_deployment_time_correlation_including_post_onset():
    result = analyze_deployments(get_sample("Failed deployment"))
    assert [e["minutes_from_onset"] for e in result.details["events"]] == [-1, 2]
    assert all(e["within_correlation_window"] for e in result.details["events"])
    assert "not proof" in result.limitations[0]


def test_far_deployment_not_correlated():
    incident = get_sample("Failed deployment")
    incident.started_at = incident.started_at.replace(day=23)
    assert not any(
        e["within_correlation_window"] for e in analyze_deployments(incident).details["events"]
    )


@pytest.mark.parametrize("value", [-1, 101, float("nan"), float("inf"), True])
def test_bad_percentage_values_rejected(value):
    data = get_sample("CPU saturation").model_dump(mode="json")
    data["metrics"][0]["value"] = value
    with pytest.raises(ValidationError):
        Incident.model_validate(data)


@pytest.mark.parametrize(
    "field", ["started_at", "metric_timestamp", "log_timestamp", "deployment_timestamp"]
)
def test_naive_timestamps_rejected(field):
    data = get_sample("HTTP 500 errors").model_dump(mode="json")
    if field == "started_at":
        data[field] = "2026-10-22T09:00:00"
    else:
        array = {
            "metric_timestamp": "metrics",
            "log_timestamp": "logs",
            "deployment_timestamp": "deployments",
        }[field]
        data[array][0]["timestamp"] = "2026-10-22T09:00:00"
    with pytest.raises(ValidationError):
        Incident.model_validate(data)
