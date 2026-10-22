"""Compare event timestamps with incident onset; correlation is not causation."""

from src.models import Evidence, Incident, ToolResult


def analyze_deployments(incident: Incident) -> ToolResult:
    facts, events = [], []
    for index, event in enumerate(incident.deployments, 1):
        delta = (event.timestamp - incident.started_at).total_seconds() / 60
        within_window = -60 <= delta <= 15
        events.append(
            {
                "version": event.version,
                "status": event.status,
                "minutes_from_onset": round(delta, 2),
                "within_correlation_window": within_window,
            }
        )
        facts.append(
            Evidence(
                id=f"D{index}",
                tool="deployments",
                source=incident.data_source,
                observation=f"Version {event.version} {event.status} at {event.timestamp.isoformat()} "
                f"({delta:+.1f} minutes from incident onset); "
                f"within [-60,+15] minute correlation window: {within_window}. {event.details}",
            )
        )
    limitations = [
        "Temporal proximity is a correlation, not proof that a deployment caused the incident.",
        "The correlation window is a demo heuristic: 60 minutes before to 15 minutes after onset.",
    ]
    if not incident.deployments:
        limitations.append("No deployment events were supplied.")
    return ToolResult(
        tool="deployments", evidence=facts, limitations=limitations, details={"events": events}
    )
