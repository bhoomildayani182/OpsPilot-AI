# OpsPilot AI execution checklist

Verified October 22, 2026. Details and measured results: [verification](docs/verification.md).

- [x] Read official About page and detailed Rules; confirm license, tags and video hosts.
- [x] Verify official Decider API, model ID, schema and supported local runtime.
- [x] Create Git repository and isolated Python 3.13 app/model environments.
- [x] Install dependencies; load actual Decider 2B weights on MLX.
- [x] Implement three read-only diagnostics and four fixed synthetic scenarios.
- [x] Implement typed tool selection, model provenance checks and abstention policy.
- [x] Run real Decider inference for all four scenarios; save exact request/response traces.
- [x] Validate those real traces against installed official Decider schema.
- [x] Execute real Strands + Amazon Bedrock reporting for two incidents using an approved profile.
- [x] Review/fix citation feedback, overstatements and causal uncertainty; regenerate valid reports.
- [x] Run Streamlit; exercise CPU and failed-deployment decisions in browser.
- [x] Pass 61 automated tests; 1 optional app-environment check skipped and separately verified.
- [x] Pass lint, formatting, compilation and dependency consistency checks.
- [x] Write setup, architecture diagram, reusable pattern, security and compliance documentation.
- [x] Prepare Builder Center article draft with actual findings and a 2:45 demo script.
- [x] Complete focused secret scan and repository contents review; confirm credentials and caches are ignored.
- [x] Explain dashboard fields, confidence scores and evidence IDs in plain language.
- [x] Fix header spacing, button contrast, responsive cards and clipped mobile controls.
- [x] Clear stale findings when inputs change; verify desktop/mobile layouts and a new real AI run.
- [x] Capture fresh end-to-end runs with safe AWS request receipts; add an honest Integration proof view.
- [x] Verify proof tab in browser and package the real runs, tests, screenshot and integrity manifest.
- [ ] Publish public GitHub repository (authentication works; publication pending review).
- [ ] Record and publish public video under three minutes.
- [ ] Publish Builder Center article, add final links/tags, register and submit.

## External review actions

The entrant must confirm eligibility and accept terms personally. The source is
Apache-2.0. The reusable pattern is #tool-selection; include #strands-decider-2b.
Accepted video hosts: YouTube, Vimeo, Facebook Video, Youku. Deadline displayed:
October 23, 2026 11:59 PM PDT = October 24, 2026 12:29 PM IST.

Optional CloudWatch ingestion is deferred; no production telemetry was accessed.
