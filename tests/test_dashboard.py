from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.data.sample_incidents import get_sample


@pytest.mark.parametrize("scenario", ["CPU saturation", "Failed deployment"])
def test_dashboard_two_incidents_and_export(scenario):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=20
    ).run()
    assert not app.exception
    app.selectbox[0].select(scenario).run()
    assert app.text_area[0].value == get_sample(scenario).title
    app.button(key="investigate").click().run()
    assert not app.exception
    assert app.session_state["investigation"].selected_tools == ["metrics", "logs", "deployments"]
    assert any("No AI tool decision or Bedrock report" in item.value for item in app.warning)
    assert (
        app.session_state["investigation"].to_dict()["incident"]["data_source"]
        == "synthetic sample"
    )
    assert len(app.get("download_button")) == 1


def test_invalid_json_does_not_start_investigation():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=20
    ).run()
    app.text_area[1].set_value("not-json").run()
    app.button(key="investigate").click().run()
    assert not app.exception
    assert "Investigation could not start" in app.error[0].value


def test_model_unavailable_ui_has_no_mock_fallback(monkeypatch):
    from src.decider import DeciderError

    def unavailable(self):
        raise DeciderError("Server unavailable for UI test")

    monkeypatch.setattr("src.decider.DeciderClient.health", unavailable)
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=20
    ).run()
    app.radio(key="investigation_mode").set_value("Decider 2B + Bedrock").run()
    app.button(key="investigate").click().run()
    assert not app.exception
    assert any("Server unavailable" in error.value for error in app.error)


@pytest.mark.parametrize("changed_input", ["scenario", "description", "mode"])
def test_changing_inputs_clears_previous_findings(changed_input):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=20
    ).run()
    app.button(key="investigate").click().run()
    assert app.session_state["investigation"]
    if changed_input == "scenario":
        app.selectbox[0].select("Failed deployment").run()
    elif changed_input == "description":
        app.text_area[0].set_value("New incident: deployment failed").run()
    else:
        app.radio(key="investigation_mode").set_value("Decider 2B + evidence only").run()
    assert "investigation" not in app.session_state
    assert not app.exception


def test_report_view_renders_recorded_real_run_with_readable_evidence(monkeypatch):
    # Recorded successful integration output tests presentation without new AWS calls.
    import json

    from src.agent import Investigation
    from src.decider import Decision
    from src.models import Report, ToolResult

    root = Path(__file__).resolve().parents[1]
    saved = json.loads((root / "artifacts/bedrock-results.json").read_text())[0]
    run = Investigation(
        mode=saved["mode"],
        incident=saved["incident"],
        selected_tools=saved["selected_tools"],
        results=[ToolResult.model_validate(item) for item in saved["results"]],
        decision=Decision(**saved["decision"]),
        report=Report.model_validate(saved["report"]),
        report_metadata=saved["report_metadata"],
    )
    monkeypatch.setattr("src.agent.investigate", lambda *args, **kwargs: run)
    app = AppTest.from_file(root / "app.py", default_timeout=20).run()
    app.radio(key="investigation_mode").set_value("Decider 2B + Bedrock").run()
    app.button(key="investigate").click().run()
    assert not app.exception
    assert app.session_state["investigation"].report.confidence == "low"
    assert len(app.get("download_button")) == 1
    assert any("M1 — CPU usage" in item.value for item in app.caption)


def test_live_mode_blocks_investigation_until_current_selection_fetched(monkeypatch):
    monkeypatch.setattr(
        "boto3.Session",
        lambda *args, **kwargs: type("Session", (), {"available_profiles": ["test"]})(),
    )
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=20
    ).run()
    app.radio(key="data_origin").set_value("Live AWS EC2 metrics").run()
    app.button(key="investigate").click().run()
    assert not app.exception
    assert any("Fetch real CloudWatch" in e.value for e in app.error)
    assert "investigation" not in app.session_state


def test_live_fetch_and_changed_window_clears_previous_data(monkeypatch):
    from datetime import UTC, datetime

    from src.models import Incident

    monkeypatch.setattr(
        "boto3.Session",
        lambda *args, **kwargs: type("Session", (), {"available_profiles": ["test"]})(),
    )
    monkeypatch.setattr(
        "src.aws_telemetry.AwsTelemetry.discover",
        lambda self: {
            "account_suffix": "1234",
            "instances": [{"id": "i-test", "name": "web", "state": "running"}],
        },
    )
    monkeypatch.setattr(
        "src.aws_telemetry.AwsTelemetry.fetch_cpu",
        lambda *args: (
            Incident(
                title="Live CPU incident",
                started_at=datetime.now(UTC),
                data_source="live CloudWatch",
                metrics=[{"name": "cpu_percent", "value": 10.0, "timestamp": datetime.now(UTC)}],
            ),
            {"instance_id": "i-test", "request_id": "receipt-test"},
        ),
    )
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=20
    ).run()
    app.radio(key="data_origin").set_value("Live AWS EC2 metrics").run()
    next(b for b in app.button if b.label == "Connect account and list EC2 instances").click().run()
    next(b for b in app.button if b.label == "Fetch real CPU data").click().run()
    app.button(key="investigate").click().run()
    assert not app.exception
    assert app.session_state["investigation"].incident["data_source"] == "live CloudWatch"
    assert app.session_state["investigation"].ingestion_metadata["request_id"] == "receipt-test"
    # Changing a selection must not silently investigate the previous snapshot.
    app.time_input[0].set_value(
        app.time_input[0].value.replace(minute=(app.time_input[0].value.minute + 1) % 60)
    ).run()
    assert "investigation" not in app.session_state
    app.button(key="investigate").click().run()
    assert any("Fetch real CloudWatch" in e.value for e in app.error)
