from unittest.mock import Mock

from src.agent import investigate, preview
from src.data.sample_incidents import get_sample
from src.demo_report import SampleReportGenerator, is_sample_report
from src.models import Incident
from tests.test_decider import client_for


def test_sample_report_uses_current_evidence_and_never_claims_bedrock():
    incident = get_sample("CPU saturation")
    incident.metrics[0].value = 12.0
    results = preview(incident, ["metrics"]).results
    reporter = SampleReportGenerator()
    report = reporter.generate(incident, ["metrics"], results)
    assert f"Average: {results[0].details['cpu_percent']['mean']:g}%" in report.incident_summary
    assert report.severity == "unknown" and report.confidence == "low"
    assert not report.potential_root_causes
    assert is_sample_report(reporter.last_metadata)
    assert reporter.last_metadata["bedrock_called"] is False
    assert reporter.last_metadata["aws_responses"] == []
    assert reporter.last_metadata["structured_output_validated"] is False


def test_sample_report_empty_evidence_does_not_invent_findings():
    incident = get_sample("Failed deployment")
    incident = Incident(title="Investigate missing telemetry", started_at=incident.started_at)
    report = SampleReportGenerator().generate(incident, [], [])
    assert report.severity_rationale.evidence_ids == []
    assert "No matching observations" in report.incident_summary
    assert report.additional_information_required


def test_sample_mode_keeps_real_decider_adapter_and_allowlisted_evidence(
    settings, health, response
):
    response["answers"]["also_logs"]["noul"] = 0.1
    run = investigate(
        get_sample("CPU saturation"),
        client_for(settings, health, response),
        SampleReportGenerator(),
    )
    assert run.decision is not None
    assert run.selected_tools == ["metrics"]
    assert [r.tool for r in run.results] == ["metrics"]
    assert run.report and is_sample_report(run.report_metadata)
    assert "no Bedrock call" in run.mode


def test_decider_abstention_prevents_even_sample_report(settings, health, response):
    response["answers"]["primary_tool"].update(
        choice="clarify",
        probabilities={"metrics": 0.05, "logs": 0.05, "deployments": 0.05, "clarify": 0.85},
    )
    reporter = Mock(spec=SampleReportGenerator)
    run = investigate(
        get_sample("CPU saturation"), client_for(settings, health, response), reporter
    )
    reporter.generate.assert_not_called()
    assert not run.results and run.report is None
