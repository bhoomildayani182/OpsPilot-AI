"""Focused pre-publication scan of Git-visible source/artifacts, never secret values."""

import json
import re
import subprocess
from pathlib import Path

PATTERNS = {
    "AWS access key": re.compile(rb"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    "AWS secret assignment": re.compile(rb"(?im)^\s*aws_secret_access_key\s*[=:]\s*\S{30,}"),
}


def main():
    # Includes tracked files and nonignored new files, without scanning local caches.
    files = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"]
    ).split(b"\0")
    findings, scanned = [], 0
    for raw in sorted(set(files)):
        if not raw:
            continue
        path = Path(raw.decode())
        if not path.is_file():
            continue
        data = path.read_bytes()
        scanned += 1
        for label, pattern in PATTERNS.items():
            if pattern.search(data):
                findings.append({"file": str(path), "kind": label})
    result = {
        "files_scanned": scanned,
        "findings": findings,
        "scope": "Focused AWS/GitHub/private-key patterns in Git-visible files; not an exhaustive secret detector.",
    }
    Path("artifacts/security-scan.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
