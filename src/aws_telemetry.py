"""Explicit, bounded, read-only EC2 discovery and CloudWatch CPU ingestion."""

import math
from datetime import UTC, datetime

import boto3
from botocore.config import Config

from src.models import Incident


class TelemetryError(RuntimeError):
    pass


class AwsTelemetry:
    def __init__(self, profile, region, session=None):
        self.session = session or boto3.Session(profile_name=profile, region_name=region)
        self.region = region
        self.config = Config(connect_timeout=5, read_timeout=15, retries={"total_max_attempts": 2})

    def client(self, name):
        return self.session.client(name, config=self.config)

    def discover(self):
        identity = self.client("sts").get_caller_identity()
        ec2 = self.client("ec2")
        instances = []
        for page in ec2.get_paginator("describe_instances").paginate(
            Filters=[
                {
                    "Name": "instance-state-name",
                    "Values": ["running", "stopped", "pending", "stopping"],
                }
            ],
            PaginationConfig={"MaxItems": 200, "PageSize": 100},
        ):
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
                    instances.append(
                        {
                            "id": instance["InstanceId"],
                            "name": tags.get("Name", "Unnamed"),
                            "state": instance["State"]["Name"],
                        }
                    )
        return {
            "account_suffix": identity["Account"][-4:],
            "inventory_fetched_at_utc": datetime.now(UTC).isoformat(),
            "region": self.region,
            "instances": instances,
            "limit": 200,
        }

    def fetch_cpu(self, instance_id, start, end):
        if start.tzinfo is None or end.tzinfo is None:
            raise TelemetryError("Choose start and end times with a timezone.")
        seconds = (end - start).total_seconds()
        if seconds <= 0 or seconds > 86400:
            raise TelemetryError(
                "Choose a time window greater than zero and no longer than 24 hours."
            )
        if end > datetime.now(UTC):
            raise TelemetryError("The end time must not be in the future.")
        period = max(300, math.ceil(seconds / 500 / 60) * 60)
        response = self.client("cloudwatch").get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=period,
            Statistics=["Average"],
            Unit="Percent",
        )
        points = sorted(response.get("Datapoints", []), key=lambda p: p["Timestamp"])
        if not points:
            raise TelemetryError(
                "CloudWatch returned no CPU samples for this instance and time window. Try a recent window when the instance was running."
            )
        incident = Incident(
            title=f"Investigate CPU measurements for EC2 instance {instance_id}.",
            started_at=start,
            data_source="live CloudWatch",
            metrics=[
                {"name": "cpu_percent", "timestamp": p["Timestamp"], "value": p["Average"]}
                for p in points
            ],
        )
        return incident, {
            "source": "Amazon CloudWatch",
            "region": self.region,
            "instance_id": instance_id,
            "namespace": "AWS/EC2",
            "metric": "CPUUtilization",
            "statistic": "Average",
            "period_seconds": period,
            "window_start_utc": start.isoformat(),
            "window_end_utc": end.isoformat(),
            "fetched_at_utc": datetime.now(UTC).isoformat(),
            "samples": len(points),
            "request_id": response.get("ResponseMetadata", {}).get("RequestId"),
            "limitations": [
                "CPU averages only; no memory, application logs or deployment events collected.",
                "EC2 inventory does not identify which application is installed or running.",
            ],
        }


def safe_aws_error(exc):
    from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

    if isinstance(exc, TelemetryError):
        return str(exc)
    if isinstance(exc, (NoCredentialsError, ProfileNotFound)):
        return "AWS credentials are unavailable. Configure or refresh the selected profile."
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"AccessDenied", "AccessDeniedException", "UnauthorizedOperation"}:
            return "AWS denied this read request. The selected profile needs EC2 DescribeInstances and CloudWatch GetMetricStatistics access."
        if code in {
            "ExpiredToken",
            "ExpiredTokenException",
            "InvalidClientTokenId",
            "UnrecognizedClientException",
        }:
            return "AWS credentials have expired or are invalid. Refresh the selected profile."
    return "Could not read AWS telemetry. Check profile access, region and network connectivity. No resource was created."
