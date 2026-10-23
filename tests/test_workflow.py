from unittest.mock import Mock

import pytest

from src.agent import investigate, preview
from src.bedrock_analyzer import BedrockAnalyzer, ReportError, validate_report
from src.config import Settings
from src.data.sample_incidents import get_sample
from src.models import Report
from tests.test_decider import client_for


def test_preview_is_explicitly_manual():
    run = preview(get_sample("CPU saturation"), ["metrics"])
    assert run.decision is None and run.report is None
    assert "no AI" in run.mode
    assert run.selected_tools == ["metrics"]
    assert run.to_dict()["results"][0]["evidence"]


def test_preview_allowlist_blocks_arbitrary_execution():
    with pytest.raises(ValueError):
        preview(get_sample("CPU saturation"), ["shell"])


def test_decider_seam_only_executes_selected_tools_and_reporter_sees_those_facts(
    settings, health, response, report_dict
):
    response["answers"]["also_logs"]["noul"] = 0.1
    reporter = Mock()
    reporter.generate.return_value = Report.model_validate(report_dict)
    run = investigate(
        get_sample("CPU saturation"), client_for(settings, health, response), reporter
    )
    assert [r.tool for r in run.results] == ["metrics"]
    assert run.report is not None
    assert reporter.generate.call_args.args[1] == ["metrics"]
    assert reporter.generate.call_args.args[2] == run.results


def test_abstention_never_calls_reporter(settings, health, response):
    answer = response["answers"]["primary_tool"]
    answer.update(
        choice="clarify",
        probabilities={"metrics": 0.05, "logs": 0.05, "deployments": 0.05, "clarify": 0.85},
    )
    reporter = Mock()
    run = investigate(
        get_sample("CPU saturation"), client_for(settings, health, response), reporter
    )
    assert not run.results
    reporter.generate.assert_not_called()


def test_bedrock_failure_preserves_evidence(settings, health, response):
    reporter = Mock()
    reporter.generate.side_effect = ReportError("Access unavailable")
    progress = []
    run = investigate(
        get_sample("CPU saturation"),
        client_for(settings, health, response),
        reporter,
        on_progress=progress.append,
    )
    assert run.results and not run.report
    assert run.report_error == "Access unavailable"
    assert len(progress) == 3
    assert "Decider" in progress[0]
    assert "checks" in progress[1]
    assert "Bedrock" in progress[2]


def test_reject_fabricated_evidence_ids(report_dict):
    report_dict["potential_root_causes"][0]["evidence_ids"] = ["INVENTED"]
    results = preview(get_sample("CPU saturation"), ["metrics"]).results
    with pytest.raises(ReportError, match="not observed"):
        validate_report(Report.model_validate(report_dict), results)


def test_reject_uncited_claim_when_evidence_exists(report_dict):
    report_dict["severity_rationale"]["evidence_ids"] = []
    with pytest.raises(ReportError, match="without evidence"):
        validate_report(
            Report.model_validate(report_dict),
            preview(get_sample("CPU saturation"), ["metrics"]).results,
        )


def test_unknown_severity_feedback_identifies_missing_citation_field(report_dict):
    report_dict.update(severity="unknown", confidence="low", potential_root_causes=[])
    report_dict["severity_rationale"]["evidence_ids"] = []
    with pytest.raises(ReportError, match="severity_rationale") as rejected:
        validate_report(
            Report.model_validate(report_dict),
            preview(get_sample("CPU saturation"), ["metrics"]).results,
        )
    assert "including when severity is unknown" in str(rejected.value)


def test_no_evidence_does_not_support_root_cause(report_dict):
    report_dict["severity_rationale"]["evidence_ids"] = []
    report_dict["potential_root_causes"] = []
    with pytest.raises(ReportError, match="No observed evidence"):
        validate_report(Report.model_validate(report_dict), [])


def test_structured_report_adapter_receives_only_observed_tools(settings, report_dict):
    fake_agent = Mock()
    fake_agent.return_value.structured_output = Report.model_validate(report_dict)
    analyzer = BedrockAnalyzer(settings, agent_factory=lambda: fake_agent)
    run = preview(get_sample("CPU saturation"), ["metrics"])
    report = analyzer.generate(get_sample("CPU saturation"), ["metrics"], run.results)
    assert report.severity == "high"
    prompt = fake_agent.call_args.args[0]
    assert "M1" in prompt and "L1" not in prompt


def test_missing_model_configuration_explained():
    with pytest.raises(ReportError, match="BEDROCK_MODEL_ID"):
        BedrockAnalyzer(Settings()).generate(get_sample("CPU saturation"), [], [])


def test_daily_quota_error_is_actionable_without_raw_provider_details(settings):
    agent = Mock(
        side_effect=RuntimeError("Too many tokens per day, please wait before trying again")
    )
    analyzer = BedrockAnalyzer(settings, agent_factory=lambda: agent)
    with pytest.raises(ReportError, match="daily token quota"):
        analyzer.generate(
            get_sample("CPU saturation"),
            ["metrics"],
            preview(get_sample("CPU saturation"), ["metrics"]).results,
        )


def test_single_diagnostic_family_cannot_claim_medium_causal_confidence(report_dict):
    report_dict["confidence"] = "medium"
    with pytest.raises(ReportError, match="causal confidence must be low"):
        validate_report(
            Report.model_validate(report_dict),
            preview(get_sample("CPU saturation"), ["metrics"]).results,
        )


def test_grounding_validator_is_in_the_sdk_output_schema(settings, report_dict):
    from pydantic import ValidationError

    agent = Mock()
    agent.return_value.structured_output = Report.model_validate(report_dict)
    analyzer = BedrockAnalyzer(settings, agent_factory=lambda: agent)
    results = preview(get_sample("CPU saturation"), ["metrics"]).results
    analyzer.generate(get_sample("CPU saturation"), ["metrics"], results)
    bound_schema = agent.call_args.kwargs["structured_output_model"]
    report_dict["potential_root_causes"][0]["evidence_ids"] = ["FABRICATED"]
    with pytest.raises(ValidationError, match="Available evidence IDs"):
        bound_schema.model_validate(report_dict)
