from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.agent import investigate
from src.bedrock_analyzer import ReportError, capture_receipt
from src.data.sample_incidents import get_sample
from tests.test_decider import client_for


def test_receipt_excludes_headers_credentials_and_raw_provider_message():
    receipts = []
    capture_receipt(
        receipts,
        parsed={
            "ResponseMetadata": {
                "RequestId": "aws-request-123",
                "HTTPStatusCode": 403,
                "HTTPHeaders": {"authorization": "must-not-export"},
            },
            "Error": {"Code": "AccessDeniedException", "Message": "private-account-details"},
            "Credentials": "must-not-export",
        },
        model=SimpleNamespace(name="ConverseStream"),
        context={"credentials": "must-not-export"},
    )
    assert receipts[0]["request_id"] == "aws-request-123"
    assert receipts[0]["error_code"] == "AccessDeniedException"
    assert receipts[0]["http_status"] == 403
    assert "must-not-export" not in str(receipts)
    assert "private-account-details" not in str(receipts)


def test_failed_report_keeps_receipt_without_claiming_valid_report(settings, health, response):
    reporter = Mock()
    reporter.generate.side_effect = ReportError("Report unavailable")
    reporter.last_metadata = {
        "structured_output_validated": False,
        "aws_responses": [{"request_id": "request-123", "http_status": 200}],
    }
    run = investigate(
        get_sample("CPU saturation"), client_for(settings, health, response), reporter
    )
    assert run.report is None
    assert run.report_metadata == reporter.last_metadata


def test_report_validation_failure_is_not_misreported_as_authentication(settings):
    from pydantic import ValidationError

    from src.agent import preview
    from src.bedrock_analyzer import BedrockAnalyzer
    from src.models import Report

    try:
        Report.model_validate({})
    except ValidationError as exc:
        agent = Mock(side_effect=exc)
    analyzer = BedrockAnalyzer(settings, agent_factory=lambda: agent)
    with pytest.raises(ReportError, match="required format or evidence checks"):
        analyzer.generate(
            get_sample("CPU saturation"),
            ["metrics"],
            preview(get_sample("CPU saturation"), ["metrics"]).results,
        )
    assert analyzer.last_metadata["structured_output_validated"] is False
    assert analyzer.last_metadata["failure_type"] == "ValidationError"


def test_missing_structured_output_is_rejected_explicitly(settings):
    from src.agent import preview
    from src.bedrock_analyzer import BedrockAnalyzer

    agent = Mock()
    agent.return_value.structured_output = None
    analyzer = BedrockAnalyzer(settings, agent_factory=lambda: agent)
    with pytest.raises(ReportError, match="six-turn limit"):
        analyzer.generate(
            get_sample("CPU saturation"),
            ["metrics"],
            preview(get_sample("CPU saturation"), ["metrics"]).results,
        )
    assert analyzer.last_metadata["failure_type"] == "MissingStructuredReport"
    assert analyzer.last_metadata["structured_output_validated"] is False
