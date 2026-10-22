"""Four fixed synthetic fixtures, deliberately separate from live AWS telemetry."""

from copy import deepcopy

from src.models import Incident

BASE = "2026-10-22T09:"


def metric(name, values):
    return [
        {"name": name, "timestamp": f"{BASE}{minute:02d}:00Z", "value": value}
        for minute, value in zip([0, 2, 4, 6], values, strict=True)
    ]


def log(minute, message, level="ERROR"):
    return {"timestamp": f"{BASE}{minute:02d}:00Z", "level": level, "message": message}


def deploy(minute, status, version, details):
    return {
        "timestamp": f"{BASE}{minute:02d}:00Z",
        "status": status,
        "version": version,
        "details": details,
    }


SAMPLES = {
    "CPU saturation": {
        "title": "EC2 CPU utilization is above 90%; investigate resource saturation.",
        "metrics": metric("cpu_percent", [88, 94, 97, 96])
        + metric("memory_percent", [54, 55, 56, 55]),
        "logs": [log(2, "Worker queue is growing", "WARN")],
        "deployments": [],
    },
    "HTTP 500 errors": {
        "title": "The checkout application returns HTTP 500 errors after a release.",
        "metrics": metric("error_rate_percent", [0.2, 6, 11, 12]),
        "logs": [
            log(1, "HTTP 500 POST /checkout NullReferenceException in PaymentHandler"),
            log(3, "HTTP 500 POST /checkout NullReferenceException in PaymentHandler"),
        ],
        "deployments": [deploy(0, "succeeded", "v1.8.0", "Checkout release completed.")],
    },
    "Failed deployment": {
        "title": "A deployment failed; investigate the release events and startup failure.",
        "metrics": [],
        "logs": [
            log(1, "StartupException: required environment variable PAYMENT_ENDPOINT missing")
        ],
        "deployments": [
            deploy(0, "failed", "v1.9.0", "Health check failed during rollout."),
            deploy(3, "rolled_back", "v1.8.0", "Previous version restored by the release system."),
        ],
    },
    "Database timeouts": {
        "title": "The application is slow and database timeouts appear in logs.",
        "metrics": metric("latency_ms", [300, 1800, 2500, 3000])
        + metric("db_connections_percent", [72, 89, 96, 99]),
        "logs": [
            log(2, "DatabaseTimeoutException: query timed out after 2000ms"),
            log(4, "Connection pool exhausted; request timed out"),
        ],
        "deployments": [deploy(0, "succeeded", "v2.0.0", "Database client settings updated.")],
    },
}


def get_sample(name: str) -> Incident:
    return Incident.model_validate(
        {
            "started_at": "2026-10-22T09:01:00Z",
            "data_source": "synthetic sample",
            **deepcopy(SAMPLES[name]),
        }
    )
