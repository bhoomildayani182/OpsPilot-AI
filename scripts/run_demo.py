"""Repeatable preview / genuine Decider / Bedrock runs with machine-readable evidence."""

import argparse
import json
from pathlib import Path

from src.agent import TOOLS, investigate, preview
from src.bedrock_analyzer import BedrockAnalyzer
from src.config import Settings
from src.data.sample_incidents import SAMPLES, get_sample
from src.decider import DeciderClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["preview", "decider", "bedrock"], default="preview")
    parser.add_argument("--scenario", choices=list(SAMPLES), action="append")
    parser.add_argument("--output", default="artifacts/demo-results.json")
    args = parser.parse_args()
    settings = Settings.from_env()
    runs = []
    for scenario in args.scenario or list(SAMPLES):
        incident = get_sample(scenario)
        if args.mode == "preview":
            run = preview(incident, list(TOOLS))
        else:
            reporter = BedrockAnalyzer(settings) if args.mode == "bedrock" else None
            run = investigate(incident, DeciderClient(settings), reporter)
        runs.append({"scenario": scenario, **run.to_dict()})
        print(
            f"{scenario}: tools={run.selected_tools}; report={'yes' if run.report else 'no'}; error={run.report_error}",
            flush=True,
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(runs, indent=2))
    if args.mode == "bedrock" and any(run["report"] is None for run in runs):
        raise SystemExit("Bedrock verification incomplete; inspect saved evidence.")
    if args.mode == "decider" and any(not run["selected_tools"] for run in runs):
        raise SystemExit("Decider abstained for a scenario; inspect saved decision trace.")


if __name__ == "__main__":
    main()
