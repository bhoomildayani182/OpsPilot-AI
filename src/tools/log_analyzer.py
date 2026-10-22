"""Extract literal error evidence; log text is data, never executable instructions."""

import re
from collections import Counter

from src.models import Evidence, Incident, ToolResult

PATTERNS = {
    "timeout": r"timeout|timed\s+out",
    "exception": r"exception|traceback",
    "http_500": r"\b500\b",
    "connection": r"connection refused|pool exhausted|too many connections",
}


def analyze_logs(incident: Incident) -> ToolResult:
    facts, counts = [], Counter()
    for index, entry in enumerate(incident.logs, 1):
        matches = [
            name for name, pattern in PATTERNS.items() if re.search(pattern, entry.message, re.I)
        ]
        counts.update(matches)
        if matches or entry.level in {"ERROR", "CRITICAL"}:
            facts.append(
                Evidence(
                    id=f"L{index}",
                    tool="logs",
                    source=incident.data_source,
                    observation=f"{entry.timestamp.isoformat()} [{entry.level}] {entry.message}",
                )
            )
    limitations = [
        "Matches describe supplied log lines only. Their frequency is not a service error rate.",
        "Absence of a matched line does not prove absence of errors.",
    ]
    if not incident.logs:
        limitations.append("No application logs were supplied.")
    return ToolResult(
        tool="logs",
        evidence=facts,
        limitations=limitations,
        details={
            "total_lines": len(incident.logs),
            "matching_lines": len(facts),
            "patterns": dict(counts),
        },
    )
