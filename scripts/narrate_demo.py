"""Create male Amazon Polly narration with an explicitly selected authorized profile."""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import boto3
from botocore.config import Config


def narrate(plan_path, output, profile="bhoomil", region="us-west-2"):
    plan = json.loads(plan_path.read_text())
    client = boto3.Session(profile_name=profile, region_name=region).client(
        "polly",
        config=Config(connect_timeout=5, read_timeout=60, retries={"total_max_attempts": 1}),
    )
    receipts = []
    output.mkdir(parents=True, exist_ok=True)
    for chapter in plan:
        text = chapter["narration"]
        if len(text) > 2900:
            raise ValueError("Narration chapter is too long")
        folder = output / chapter["capture"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "narration.txt").write_text(text)
        response = client.synthesize_speech(
            Engine="generative",
            VoiceId="Stephen",
            LanguageCode="en-US",
            OutputFormat="mp3",
            SampleRate="24000",
            Text=text,
            TextType="text",
        )
        with response["AudioStream"] as stream:
            audio = stream.read()
        (folder / "voice.mp3").write_bytes(audio)
        receipts.append(
            {
                "chapter": chapter["capture"],
                "request_id": response["ResponseMetadata"]["RequestId"],
                "characters": len(text),
                "audio_bytes": len(audio),
                "audio_sha256": hashlib.sha256(audio).hexdigest(),
            }
        )
    (output / "narration-manifest.json").write_text(
        json.dumps(
            {
                "created_at_utc": datetime.now(UTC).isoformat(),
                "profile": profile,
                "region": region,
                "provider": "Amazon Polly",
                "voice": "Stephen",
                "gender": "Male",
                "engine": "generative",
                "synthetic": True,
                "requests": receipts,
            },
            indent=2,
        )
    )
    print(f"Generated {len(receipts)} male narration chapters; no AWS resources provisioned.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", default="bhoomil")
    parser.add_argument("--region", default="us-west-2")
    args = parser.parse_args()
    narrate(args.plan, args.output, args.profile, args.region)
