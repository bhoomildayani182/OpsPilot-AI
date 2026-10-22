"""Validated inputs and report contract shared by the UI, tools, and model adapter."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Metric(Record):
    name: Literal[
        "cpu_percent",
        "memory_percent",
        "latency_ms",
        "error_rate_percent",
        "db_connections_percent",
    ]
    timestamp: datetime
    value: float = Field(ge=0, strict=True)

    @field_validator("timestamp")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            raise ValueError("timestamps must include a timezone")
        return value


class LogEntry(Record):
    timestamp: datetime
    level: Literal["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
    message: str = Field(min_length=1, max_length=2000)
    _tz = field_validator("timestamp")(Metric.timezone_required.__func__)


class Deployment(Record):
    timestamp: datetime
    status: Literal["succeeded", "failed", "rolled_back", "in_progress"]
    version: str = Field(min_length=1, max_length=100)
    details: str = Field(max_length=1000)
    _tz = field_validator("timestamp")(Metric.timezone_required.__func__)


class Incident(Record):
    title: str = Field(min_length=5, max_length=2000)
    started_at: datetime
    data_source: Literal["synthetic sample", "user supplied", "live CloudWatch"] = "user supplied"
    metrics: list[Metric] = Field(default_factory=list, max_length=500)
    logs: list[LogEntry] = Field(default_factory=list, max_length=500)
    deployments: list[Deployment] = Field(default_factory=list, max_length=100)
    _tz = field_validator("started_at")(Metric.timezone_required.__func__)

    @field_validator("metrics")
    @classmethod
    def percentages_in_range(cls, values):
        if any(m.name.endswith("percent") and m.value > 100 for m in values):
            raise ValueError("percentage metrics must be between 0 and 100")
        return values


class Evidence(Record):
    id: str
    tool: str
    observation: str
    source: str


class ToolResult(Record):
    tool: str
    evidence: list[Evidence]
    limitations: list[str]
    details: dict = Field(default_factory=dict)


class Finding(Record):
    statement: str = Field(min_length=1, max_length=2000)
    evidence_ids: list[str] = Field(
        max_length=30,
        description="IDs of observed tool evidence supporting this finding, such as M1 or D1. Must contain at least one supplied ID when any observed evidence exists. Never invent an ID.",
    )


class Report(Record):
    incident_summary: str = Field(
        min_length=1,
        max_length=3000,
        description="Begin with what the user reports. Summarize exact supplied observations without claiming a confirmed cause, continuous monitoring, or established service impact.",
    )
    severity: Literal["critical", "high", "medium", "low", "unknown"]
    severity_rationale: Finding
    potential_root_causes: list[Finding] = Field(
        max_length=3,
        description="At most three narrowly relevant hypotheses, explicitly phrased as possible explanations. Do not assert causation from a deployment timestamp or enumerate unsupported attack/network/host-failure scenarios.",
    )
    confidence: Literal["low", "medium", "high"]
    uncertainty: list[str] = Field(min_length=1, max_length=15)
    recommended_steps: list[str] = Field(min_length=1, max_length=15)
    additional_information_required: list[str] = Field(min_length=1, max_length=15)
