"""Read-only quota/usage diagnosis and one real SDK report call; never logs credentials."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import boto3
from botocore.config import Config

import src.bedrock_analyzer as adapter
from src.agent import preview
from src.config import Settings
from src.data.sample_incidents import get_sample


def main():
    settings = Settings.from_env()
    if settings.aws_profile != "bhoomil" or settings.region != "us-west-2":
        raise SystemExit("Diagnosis requires explicit bhoomil / us-west-2 settings.")
    session = boto3.Session(profile_name="bhoomil", region_name="us-west-2")
    config = Config(connect_timeout=5, read_timeout=30, retries={"total_max_attempts": 1})
    identity = session.client("sts", config=config).get_caller_identity()
    private = Path("artifacts/private/bedrock-diagnosis")
    private.mkdir(parents=True, exist_ok=True)
    (private / "identity.json").write_text(json.dumps(identity, indent=2))
    runtime = session.client("bedrock-runtime", config=config)
    now = datetime.now(UTC)
    out = {
        "checked_at_utc": now.isoformat(),
        "configuration": {
            "profile": settings.aws_profile,
            "region": settings.region,
            "model_id": settings.bedrock_model,
            "service": runtime.meta.service_model.service_name,
            "endpoint": runtime.meta.endpoint_url,
            "operation": "ConverseStream (Strands SDK)",
            "account_suffix": identity["Account"][-4:],
            "max_output_tokens": 2400,
        },
    }
    calls = []
    original = adapter.capture_receipt

    def capture(receipts, *, parsed, model, **kwargs):
        original(receipts, parsed=parsed, model=model, **kwargs)
        # No HTTP headers, signed requests, credentials or unrestricted SDK logs.
        calls.append(
            {
                "operation": model.name,
                "error": parsed.get("Error"),
                "http_status": parsed.get("ResponseMetadata", {}).get("HTTPStatusCode"),
                "request_id": parsed.get("ResponseMetadata", {}).get("RequestId"),
            }
        )

    adapter.capture_receipt = capture
    analyzer = adapter.BedrockAnalyzer(settings)
    incident = get_sample("CPU saturation")
    try:
        report = analyzer.generate(incident, ["metrics"], preview(incident, ["metrics"]).results)
        out["report"] = report.model_dump(mode="json")
    except adapter.ReportError as exc:
        out["ui_error"] = str(exc)
    finally:
        adapter.capture_receipt = original
    out["sdk_service_responses"] = calls
    out["report_metadata"] = analyzer.last_metadata
    print("Exact SDK service responses:", json.dumps(calls), flush=True)
    quotas = session.client("service-quotas", config=config)
    matching = []
    for page in quotas.get_paginator("list_service_quotas").paginate(ServiceCode="bedrock"):
        for quota in page["Quotas"]:
            name = quota["QuotaName"].lower()
            if ("nova lite" in name and "batch" not in name) or "cross-model" in name:
                matching.append(quota)
    # Preserve exact names/codes and any AWS-supplied usage metric mapping.
    out["matching_applied_quotas"] = matching
    print(
        "Matching applied quotas:",
        json.dumps(
            [
                {
                    k: q.get(k)
                    for k in ["QuotaName", "QuotaCode", "Value", "Adjustable", "GlobalQuota"]
                }
                for q in matching
            ]
        ),
        flush=True,
    )
    cw = session.client("cloudwatch", config=config)
    metric_entries = []
    for page in cw.get_paginator("list_metrics").paginate(Namespace="AWS/Bedrock"):
        metric_entries.extend(page["Metrics"])
    wanted = {
        "InputTokenCount",
        "OutputTokenCount",
        "CacheWriteInputTokenCount",
        "CacheReadInputTokenCount",
        "Invocations",
        "InvocationThrottles",
        "InvocationClientErrors",
        "EstimatedTPMQuotaUsage",
    }
    observed = []
    for metric in metric_entries:
        dims = metric["Dimensions"]
        model_values = [d["Value"] for d in dims if d["Name"] == "ModelId"]
        if metric["MetricName"] not in wanted or not any(
            settings.bedrock_model in m for m in model_values
        ):
            continue
        result = cw.get_metric_statistics(
            Namespace="AWS/Bedrock",
            MetricName=metric["MetricName"],
            Dimensions=dims,
            StartTime=now - timedelta(days=2),
            EndTime=now,
            Period=3600,
            Statistics=["Sum"],
        )
        observed.append(
            {
                "name": metric["MetricName"],
                "dimensions": dims,
                "points": sorted(result.get("Datapoints", []), key=lambda p: p["Timestamp"]),
            }
        )
    out["cloudwatch"] = {
        "namespace": "AWS/Bedrock",
        "start_utc": (now - timedelta(days=2)).isoformat(),
        "end_utc": now.isoformat(),
        "period_seconds": 3600,
        "statistic": "Sum",
        "metrics": observed,
        "interpretation": "Missing CloudWatch series are unavailable observations, not zero usage. These regional/model metrics cannot establish the account's exact remaining cross-model daily allowance.",
    }
    aggregate = []
    for name in sorted(wanted):
        result = cw.get_metric_statistics(
            Namespace="AWS/Bedrock",
            MetricName=name,
            Dimensions=[],
            StartTime=now - timedelta(days=2),
            EndTime=now,
            Period=3600,
            Statistics=["Sum"],
        )
        aggregate.append(
            {
                "name": name,
                "dimensions": [],
                "points": sorted(result.get("Datapoints", []), key=lambda p: p["Timestamp"]),
            }
        )
    out["cloudwatch"]["aggregate_without_dimensions"] = aggregate
    (private / "full.json").write_text(json.dumps(out, indent=2, default=str))
    for quota in matching:
        quota.pop("QuotaArn", None)
    Path("artifacts/bedrock-diagnosis.json").write_text(json.dumps(out, indent=2, default=str))
    print("Diagnosis saved; CloudWatch matching series:", len(observed), flush=True)


if __name__ == "__main__":
    main()
