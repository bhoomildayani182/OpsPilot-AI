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
    assert "No AI tool decision or Bedrock report" in app.warning[0].value
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
    app.radio[0].set_value("Decider 2B + Bedrock").run()
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
        app.radio[0].set_value("Decider 2B + evidence only").run()
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
    app.radio[0].set_value("Decider 2B + Bedrock").run()
    app.button(key="investigate").click().run()
    assert not app.exception
    assert app.session_state["investigation"].report.confidence == "low"
    assert len(app.get("download_button")) == 1
    assert any("M1 — CPU usage" in item.value for item in app.caption)
