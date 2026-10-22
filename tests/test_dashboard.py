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
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["investigation"].selected_tools == ["metrics", "logs", "deployments"]
    assert "LOCAL EVIDENCE PREVIEW" in app.warning[0].value
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
    app.button[0].click().run()
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
    app.button[0].click().run()
    assert not app.exception
    assert any("Server unavailable" in error.value for error in app.error)
