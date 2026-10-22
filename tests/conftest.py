import copy

import pytest

from src.config import Settings


@pytest.fixture
def settings():
    return Settings(bedrock_model="configured-test-model")


@pytest.fixture
def health():
    return {
        "status": "ok",
        "model": "strands-decider-2B-qwen3.5-v1-2610",
        "checkpoint": "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610",
        "device": "test-double",
    }


@pytest.fixture
def response():
    return {
        "model": "strands-decider-2B-qwen3.5-v1-2610",
        "answers": {
            "primary_tool": {
                "type": "choice",
                "choice": "metrics",
                "confidence": 0.8,
                "probabilities": {
                    "metrics": 0.85,
                    "logs": 0.05,
                    "deployments": 0.05,
                    "clarify": 0.05,
                },
            },
            "also_metrics": {"type": "noul", "noul": 0.95},
            "also_logs": {"type": "noul", "noul": 0.9},
            "also_deployments": {"type": "noul", "noul": 0.1},
        },
        "usage": {"input_tokens": 123, "output_tokens": 0},
        "latency_ms": 12.3,
    }


@pytest.fixture
def report_dict():
    return copy.deepcopy(
        {
            "incident_summary": "The user reports CPU saturation.",
            "severity": "high",
            "severity_rationale": {
                "statement": "Several CPU samples exceed the demo threshold.",
                "evidence_ids": ["M1"],
            },
            "potential_root_causes": [
                {"statement": "A CPU-bound workload is a hypothesis.", "evidence_ids": ["M1"]}
            ],
            "confidence": "low",
            "uncertainty": ["Process-level data is absent."],
            "recommended_steps": [
                "Inspect per-process CPU usage using approved read-only tooling."
            ],
            "additional_information_required": ["Traffic and process metrics around onset."],
        }
    )
