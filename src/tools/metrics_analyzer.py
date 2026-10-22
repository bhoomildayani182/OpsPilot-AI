"""Compute facts from supplied samples; thresholds are explicit demo heuristics."""

from collections import defaultdict
from statistics import mean

from src.models import Evidence, Incident, ToolResult

THRESHOLDS = {
    "cpu_percent": 90,
    "memory_percent": 90,
    "latency_ms": 1000,
    "error_rate_percent": 5,
    "db_connections_percent": 85,
}


def analyze_metrics(incident: Incident) -> ToolResult:
    groups = defaultdict(list)
    for sample in incident.metrics:
        groups[sample.name].append(sample)
    facts, summaries = [], {}
    for index, (name, samples) in enumerate(sorted(groups.items()), 1):
        values = [sample.value for sample in samples]
        threshold = THRESHOLDS[name]
        above = sum(value > threshold for value in values)
        summaries[name] = {
            "min": min(values),
            "max": max(values),
            "mean": round(mean(values), 2),
            "samples": len(values),
            "above_threshold": above,
            "threshold": threshold,
        }
        facts.append(
            Evidence(
                id=f"M{index}",
                tool="metrics",
                source=incident.data_source,
                observation=f"{name}: {len(values)} samples, min={min(values):g}, max={max(values):g}, "
                f"mean={mean(values):.2f}; {above} strictly above demo threshold {threshold}. "
                f"Window {min(s.timestamp for s in samples).isoformat()} to "
                f"{max(s.timestamp for s in samples).isoformat()}.",
            )
        )
    limitations = [
        "Thresholds are demo heuristics, not service SLOs. Samples do not establish a root cause."
    ]
    if not groups:
        limitations.append(
            "No metrics were supplied; normal infrastructure health cannot be inferred."
        )
    return ToolResult(tool="metrics", evidence=facts, limitations=limitations, details=summaries)
