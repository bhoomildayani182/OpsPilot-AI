"""Package recorded evidence; never invent or replace missing successful runs."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "docs/hackathon-proof.md",
    "artifacts/hackathon-proof-runs.json",
    "artifacts/decider-results.json",
    "artifacts/test-output.txt",
    "artifacts/test-results.xml",
    "artifacts/hackathon-proof.jpg",
]


def main():
    runs = json.loads((ROOT / FILES[1]).read_text())
    if len(runs) != 2:
        raise SystemExit("Expected both recorded scenarios.")
    for run in runs:
        metadata = run.get("report_metadata") or {}
        receipts = metadata.get("aws_responses", [])
        if not (
            run.get("decision")
            and run.get("report")
            and metadata.get("provider") == "Amazon Bedrock"
            and metadata.get("structured_output_validated")
            and any(r.get("request_id") and r.get("http_status") == 200 for r in receipts)
        ):
            raise SystemExit("Incomplete integration evidence; no archive generated.")
    # Reading every file first ensures missing evidence cannot yield a partial archive.
    optional = [
        "docs/aws-usage-and-cleanup.md",
        "artifacts/live-aws-investigation.json",
        "artifacts/ec2-demo-resource.json",
        "artifacts/live-aws-selection.jpg",
        "artifacts/live-aws-proof.jpg",
        "artifacts/report-fix-verification.json",
        "artifacts/aws-logging-check.json",
    ]
    contents = {
        name: (ROOT / name).read_bytes()
        for name in [*FILES, *[n for n in optional if (ROOT / n).exists()]]
    }
    manifest = {
        "description": "Locally generated integrity hashes; not independent attestation.",
        "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()},
    }
    manifest_path = ROOT / "artifacts/hackathon-proof-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    with ZipFile(ROOT / "artifacts/hackathon-proof.zip", "w", ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            archive.writestr(name, data)
        archive.write(manifest_path, "artifacts/hackathon-proof-manifest.json")
    print("Packaged recorded integration evidence, tests, screenshots and integrity hashes.")


if __name__ == "__main__":
    main()
