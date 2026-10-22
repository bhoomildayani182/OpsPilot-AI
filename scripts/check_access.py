"""Read-only preflight. Never outputs credentials, account IDs, or tokens."""

import argparse
import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.config import Settings
from src.decider import DeciderClient, DeciderError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List active on-demand TEXT models; no inference call",
    )
    args = parser.parse_args()
    settings = Settings.from_env()
    try:
        health = DeciderClient(settings).health()
        print(f"Decider loaded: {health['model']} ({health['device']})")
    except DeciderError as exc:
        print(f"Decider pending: {exc}")
    try:
        session = boto3.Session(profile_name=settings.aws_profile, region_name=settings.region)
        session.client("sts").get_caller_identity()
        print(
            f"AWS authentication: OK in {settings.region}; profile={settings.aws_profile or 'default chain'}"
        )
        if args.list_models:
            models = session.client("bedrock").list_foundation_models(
                byOutputModality="TEXT", byInferenceType="ON_DEMAND"
            )
            print(
                json.dumps(
                    [
                        {"id": m["modelId"], "provider": m["providerName"]}
                        for m in models["modelSummaries"]
                        if m.get("modelLifecycle", {}).get("status") == "ACTIVE"
                    ],
                    indent=2,
                )
            )
    except (BotoCoreError, ClientError):
        print("AWS authentication or model listing failed; refresh credentials/check permissions.")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
