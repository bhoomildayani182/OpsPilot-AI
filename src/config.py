"""Configuration without stored credentials or implicit AWS profile selection."""

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv

MODEL_ID = "strands-decider-2B-qwen3.5-v1-2610"
CHECKPOINT = f"StrandsAgents/{MODEL_ID}"


@dataclass(frozen=True)
class Settings:
    decider_url: str = "http://127.0.0.1:8099"
    decider_model: str = MODEL_ID
    timeout: float = 120
    min_confidence: float = 0.35
    aws_profile: str | None = None
    region: str = "us-east-1"
    bedrock_model: str = ""

    def __post_init__(self):
        parsed = urlparse(self.decider_url)
        if parsed.hostname not in {"localhost", "127.0.0.1", "::1"} or parsed.scheme != "http":
            raise ValueError("This MVP requires a local Decider server over loopback HTTP.")
        if (
            parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
        ):
            raise ValueError("Decider URL must contain only the loopback host and port.")
        if not 0 <= self.min_confidence <= 1:
            raise ValueError("DECIDER_MIN_CONFIDENCE must be between 0 and 1")
        if not 1 <= self.timeout <= 300:
            raise ValueError("DECIDER_TIMEOUT_SECONDS must be between 1 and 300")

    @classmethod
    def from_env(cls):
        load_dotenv(override=False)
        return cls(
            decider_url=os.getenv("STRANDS_DECIDER_URL", "http://127.0.0.1:8099"),
            decider_model=os.getenv("DECIDER_MODEL_ID", MODEL_ID),
            timeout=float(os.getenv("DECIDER_TIMEOUT_SECONDS", "120")),
            min_confidence=float(os.getenv("DECIDER_MIN_CONFIDENCE", "0.35")),
            aws_profile=os.getenv("OPSPILOT_AWS_PROFILE") or os.getenv("AWS_PROFILE") or None,
            region=os.getenv("AWS_REGION", "us-east-1"),
            bedrock_model=os.getenv("BEDROCK_MODEL_ID", ""),
        )
