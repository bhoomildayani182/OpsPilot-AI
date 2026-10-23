from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from src.aws_telemetry import AwsTelemetry, TelemetryError, safe_aws_error


def collector():
    session = Mock()
    return AwsTelemetry("test", "us-east-1", session=session), session


def test_discovery_reads_paginated_inventory_without_write_operations():
    reader, session = collector()
    session.client.return_value.get_caller_identity.return_value = {"Account": "123456789012"}
    session.client.return_value.get_paginator.return_value.paginate.return_value = [
        {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-0123456789abcdef0",
                            "State": {"Name": "running"},
                            "Tags": [{"Key": "Name", "Value": "test-web"}],
                        }
                    ]
                }
            ]
        }
    ]
    inventory = reader.discover()
    assert inventory["account_suffix"] == "9012"
    assert inventory["instances"][0]["id"] == "i-0123456789abcdef0"
    assert [c.args[0] for c in session.client.call_args_list] == ["sts", "ec2"]
    session.client.return_value.get_paginator.assert_called_once_with("describe_instances")


def test_fetch_cpu_preserves_real_times_dimensions_and_receipt():
    reader, session = collector()
    end = datetime.now(UTC) - timedelta(minutes=1)
    start = end - timedelta(hours=1)
    session.client.return_value.get_metric_statistics.return_value = {
        "Datapoints": [{"Timestamp": end, "Average": 23.5}, {"Timestamp": start, "Average": 11.0}],
        "ResponseMetadata": {"RequestId": "real-request"},
    }
    incident, receipt = reader.fetch_cpu("i-0123456789abcdef0", start, end)
    assert incident.data_source == "live CloudWatch"
    assert [m.value for m in incident.metrics] == [11, 23.5]
    assert not incident.logs and not incident.deployments
    assert receipt["request_id"] == "real-request"
    args = session.client.return_value.get_metric_statistics.call_args.kwargs
    assert args["Dimensions"] == [{"Name": "InstanceId", "Value": "i-0123456789abcdef0"}]
    assert args["Period"] == 300 and args["StartTime"] == start and args["EndTime"] == end


@pytest.mark.parametrize("hours", [0, -1, 25])
def test_invalid_window_never_calls_aws(hours):
    reader, session = collector()
    start = datetime.now(UTC) - timedelta(hours=26)
    with pytest.raises(TelemetryError):
        reader.fetch_cpu("i-0123456789abcdef0", start, start + timedelta(hours=hours))
    session.client.assert_not_called()


def test_no_data_never_becomes_synthetic_fallback():
    reader, session = collector()
    session.client.return_value.get_metric_statistics.return_value = {"Datapoints": []}
    end = datetime.now(UTC)
    with pytest.raises(TelemetryError, match="no CPU samples"):
        reader.fetch_cpu("i-0123456789abcdef0", end - timedelta(hours=1), end)


def test_error_does_not_expose_raw_provider_message():
    error = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "private account details"}},
        "GetMetricStatistics",
    )
    assert "denied" in safe_aws_error(error)
    assert "private account" not in safe_aws_error(error)


def test_invalid_id_and_too_old_window_never_call_aws():
    reader, session = collector()
    end = datetime.now(UTC)
    with pytest.raises(TelemetryError, match="valid EC2"):
        reader.fetch_cpu("wrong-id", end - timedelta(hours=1), end)
    with pytest.raises(TelemetryError, match="last 14 days"):
        reader.fetch_cpu("i-0123456789abcdef0", end - timedelta(days=16), end - timedelta(days=15))
    session.client.assert_not_called()
