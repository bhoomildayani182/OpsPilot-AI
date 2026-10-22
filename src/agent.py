"""Enforced decision seam: Decider selection -> allowlisted diagnostics -> Bedrock."""

from collections.abc import Callable
from dataclasses import asdict, dataclass

from src.bedrock_analyzer import BedrockAnalyzer, ReportError
from src.decider import DeciderClient, Decision
from src.models import Incident, Report, ToolResult
from src.tools.deployment_analyzer import analyze_deployments
from src.tools.log_analyzer import analyze_logs
from src.tools.metrics_analyzer import analyze_metrics

TOOLS: dict[str, Callable[[Incident], ToolResult]] = {
    "metrics": analyze_metrics,
    "logs": analyze_logs,
    "deployments": analyze_deployments,
}


@dataclass
class Investigation:
    mode: str
    incident: dict
    selected_tools: list[str]
    results: list[ToolResult]
    decision: Decision | None = None
    report: Report | None = None
    report_error: str | None = None
    report_metadata: dict | None = None

    def to_dict(self):
        return {
            **asdict(self),
            "results": [r.model_dump(mode="json") for r in self.results],
            "report": self.report.model_dump(mode="json") if self.report else None,
        }


def preview(incident: Incident, selected_tools: list[str]) -> Investigation:
    if set(selected_tools) - TOOLS.keys():
        raise ValueError("Unknown diagnostic tool")
    selected_tools = list(dict.fromkeys(selected_tools))
    return Investigation(
        mode="Local evidence preview — no AI decision or Bedrock",
        incident=incident.model_dump(mode="json"),
        selected_tools=selected_tools,
        results=[TOOLS[name](incident) for name in selected_tools],
    )


def investigate(
    incident: Incident, decider: DeciderClient, reporter: BedrockAnalyzer | None
) -> Investigation:
    decision = decider.select(incident)
    if set(decision.selected_tools) - TOOLS.keys():
        raise ValueError("Decider selected a tool outside the allowlist")
    results = [TOOLS[name](incident) for name in decision.selected_tools]
    run = Investigation(
        mode="Strands Decider 2B + Amazon Bedrock",
        incident=incident.model_dump(mode="json"),
        selected_tools=decision.selected_tools,
        results=results,
        decision=decision,
    )
    if decision.needs_clarification:
        return run
    if reporter is None:
        run.mode = "Real Decider 2B + local evidence — Bedrock not requested"
        return run
    try:
        run.report = reporter.generate(incident, decision.selected_tools, results)
        metadata = getattr(reporter, "last_metadata", None)
        run.report_metadata = metadata if isinstance(metadata, dict) else None
    except ReportError as exc:
        run.report_error = str(exc)
        metadata = getattr(reporter, "last_metadata", None)
        run.report_metadata = metadata if isinstance(metadata, dict) else None
    return run
