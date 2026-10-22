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
- [x] Pass 71 automated tests; 1 optional app-environment check skipped and separately verified.
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

Live EC2/CloudWatch CPU ingestion is implemented. Only a separately authorized
disposable test instance was used; no production workload was inspected.

## Live AWS work

- [x] Add explicit profile, region, EC2 and UTC time-window selection.
- [x] Block stale or missing fetches; preserve CloudWatch provenance.
- [x] Verify actual EC2 discovery and CloudWatch CPU collection.
- [x] Process real CPU evidence through Decider and Bedrock; preserve report and receipts.
- [x] Diagnose missing structured output; three fresh CPU report tests pass after correction.
- [x] Verify browser live-data flow and cleanup of disposable demo resources.

## Screen-video request — bhoomil only

- [x] Audit hardik: no project EC2, disks or security groups; invocation logging not configured.
- [x] Switch all new reporting and demo provisioning to bhoomil/us-west-2; verify tiny Bedrock call.
- [x] Create isolated temporary recording-demo EC2 in bhoomil.
- [x] Record actual dashboard interactions: live AWS data, real Decider selection and the truthful AWS reporting quota error.
- [x] Produce a narrated, captioned 1080p MP4: 169.56 seconds; full decode and visual/audio checks passed.
- [x] Delete the recording-demo EC2, disk and security group; independently verify deletion.

- [ ] Record successful new Bedrock report in bhoomil: still blocked by AWS daily token quota, including after user access recheck. Do not claim this review video demonstrates successful reporting.
