import copy
import json

import httpx
import pytest

from src.config import Settings
from src.data.sample_incidents import get_sample
from src.decider import QUESTION, RELEVANCE, DeciderClient, DeciderError


def client_for(settings, health, payload, requests=None):
    def handler(request):
        if requests is not None:
            requests.append(request)
        return httpx.Response(200, json=health if request.url.path == "/health" else payload)

    return DeciderClient(settings, httpx.Client(transport=httpx.MockTransport(handler)))


def test_exact_official_request_and_decision_affects_executed_tool_set(settings, health, response):
    requests = []
    decision = client_for(settings, health, response, requests).select(get_sample("CPU saturation"))
    assert decision.selected_tools == ["metrics", "logs"]
    assert decision.confidence == 0.8
    assert decision.caution
    assert decision.model == settings.decider_model
    assert requests[1].url.path == "/v1/systemone"
    body = json.loads(requests[1].content)
    assert body["questions"]["primary_tool"] == QUESTION
    assert body["questions"]["also_logs"] == RELEVANCE["logs"]
    assert decision.request == body


def test_abstain_on_low_confidence(settings, health, response):
    answer = response["answers"]["primary_tool"]
    answer["probabilities"] = {"metrics": 0.4, "logs": 0.2, "deployments": 0.2, "clarify": 0.2}
    answer["confidence"] = 0.2
    decision = client_for(settings, health, response).select(get_sample("CPU saturation"))
    assert decision.needs_clarification
    assert not decision.selected_tools


def test_clarify_choice_abstains_even_when_confident(settings, health, response):
    answer = response["answers"]["primary_tool"]
    answer["choice"] = "clarify"
    answer["probabilities"]["metrics"], answer["probabilities"]["clarify"] = 0.05, 0.85
    assert (
        not client_for(settings, health, response)
        .select(get_sample("CPU saturation"))
        .selected_tools
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown_tool",
        "nan",
        "sum",
        "wrong_type",
        "wrong_model",
        "confidence",
        "wrong_argmax",
        "invalid_noul",
    ],
)
def test_malformed_response_fails_closed(settings, health, response, mutation):
    answer = response["answers"]["primary_tool"]
    if mutation == "unknown_tool":
        answer["choice"] = "run_shell"
    elif mutation == "nan":
        answer["confidence"] = "NaN"
    elif mutation == "sum":
        answer["probabilities"]["metrics"] = 0.6
    elif mutation == "wrong_type":
        answer["type"] = "score"
    elif mutation == "wrong_model":
        response["model"] = "ordinary-llm"
    elif mutation == "confidence":
        answer["confidence"] = 0.99
    elif mutation == "wrong_argmax":
        answer["choice"] = "logs"
    else:
        response["answers"]["also_logs"]["noul"] = 2
    with pytest.raises(DeciderError):
        client_for(settings, health, response).select(get_sample("CPU saturation"))


def test_health_identity_required(settings, health, response):
    health["checkpoint"] = "other-model"
    with pytest.raises(DeciderError, match="checkpoint"):
        client_for(settings, health, response).select(get_sample("CPU saturation"))


def test_network_failure_never_falls_back(settings):
    def unavailable(request):
        raise httpx.ConnectError("offline")

    client = DeciderClient(settings, httpx.Client(transport=httpx.MockTransport(unavailable)))
    with pytest.raises(DeciderError):
        client.select(get_sample("CPU saturation"))


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254",
        "https://remote.example",
        "file:///etc/passwd",
        "http://user:pass@localhost:8099",
        "http://localhost:8099/other",
    ],
)
def test_non_loopback_or_ambiguous_endpoint_rejected(url):
    with pytest.raises(ValueError):
        Settings(decider_url=url)


def test_request_matches_installed_official_schema(settings, health, response):
    # The runtime is optional for ordinary app installs. When present, validate against
    # its actual published Pydantic models, not a second handwritten wire schema.
    schema = pytest.importorskip("strands_decider.schema")
    decision = client_for(settings, health, copy.deepcopy(response)).select(
        get_sample("CPU saturation")
    )
    schema.SystemOneRequest.model_validate(decision.request)
    schema.SystemOneResponse.model_validate(decision.raw_response)


def test_app_specific_aws_profile_overrides_inherited_desktop_profile(monkeypatch):
    monkeypatch.setenv("AWS_PROFILE", "expired-desktop-profile")
    monkeypatch.setenv("OPSPILOT_AWS_PROFILE", "chosen-profile")
    assert Settings.from_env().aws_profile == "chosen-profile"
