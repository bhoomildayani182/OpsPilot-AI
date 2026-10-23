"""Plain-language labels for the dashboard; these never change diagnostic evidence."""

from src.models import ToolResult

TOOL_LABELS = {
    "metrics": "Metrics Analyzer",
    "logs": "Log Analyzer",
    "deployments": "Deployment Analyzer",
    "clarify": "Ask for more information",
}
TOOL_PURPOSES = {
    "metrics": "Checks CPU, memory, response time and other server measurements.",
    "logs": "Looks for errors, exceptions and timeouts in application messages.",
    "deployments": "Checks failed releases, rollbacks and their timing around the incident.",
}
METRIC_LABELS = {
    "cpu_percent": ("CPU usage", "%"),
    "memory_percent": ("Memory usage", "%"),
    "latency_ms": ("Response time", " ms"),
    "error_rate_percent": ("Error rate", "%"),
    "db_connections_percent": ("Database connections used", "%"),
}
MODE_LABELS = {
    "Local evidence preview": "View diagnostic findings · no AI",
    "Decider 2B + Bedrock": "Full AI investigation",
    "Decider 2B + evidence only": "AI tool selection only",
    "Decider 2B + sample report": "Demo report · real Decider 2B",
}
MODE_HELP = {
    "Local evidence preview": "You choose the checks. See facts from the supplied data without an AI report or AWS model calls.",
    "Decider 2B + Bedrock": "Decider 2B chooses the checks. Amazon Bedrock writes a report with possible causes and next steps. Uses AWS model access.",
    "Decider 2B + evidence only": "Decider 2B chooses the checks and you see their findings. No Bedrock report is requested.",
    "Decider 2B + sample report": "Real Decider 2B chooses the checks. A local template formats their actual evidence into a labelled sample report. Amazon Bedrock is not called in this mode.",
}
SCENARIO_HELP = {
    "CPU saturation": "The server's processor is busy. Check how many CPU measurements exceed the demo limit.",
    "HTTP 500 errors": "Some web requests are failing. Look for error messages and nearby release events.",
    "Failed deployment": "A software release did not finish successfully. Check the release timeline and startup errors.",
    "Database timeouts": "Requests are slow and database operations are timing out. Look at response times, connections and errors.",
    "Custom incident": "Describe your own incident and add its measurements, logs and release events below.",
}


def metric_sentence(name: str, values: dict) -> str:
    label, unit = METRIC_LABELS[name]
    return (
        f"{values['above_threshold']} of {values['samples']} samples were above the "
        f"{values['threshold']:g}{unit} demo limit. "
        f"Highest: {values['max']:g}{unit}. Average: {values['mean']:g}{unit}."
    )


def evidence_labels(results: list[ToolResult]) -> dict[str, str]:
    labels = {}
    for result in results:
        if result.tool == "metrics":
            for evidence, name in zip(result.evidence, result.details, strict=True):
                labels[evidence.id] = METRIC_LABELS[name][0]
        elif result.tool == "logs":
            labels.update({e.id: "Application log message" for e in result.evidence})
        else:
            labels.update({e.id: "Release event" for e in result.evidence})
    return labels


def source_label(source: str) -> str:
    return {
        "synthetic sample": "Sample data · not live AWS data",
        "user supplied": "Data supplied by you · no live AWS collection",
        "live CloudWatch": "Labeled CloudWatch data · supplied by you",
    }[source]


def collection_label(source: str, receipt: dict | None) -> str:
    if receipt and receipt.get("read_mode") == "recorded_snapshot":
        return "Recorded AWS snapshot · original collection time"
    if receipt:
        return "AWS data · fetched from CloudWatch"
    return source_label(source)
