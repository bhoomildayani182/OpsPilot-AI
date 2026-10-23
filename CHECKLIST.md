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

## EC2 loading and visible output fix — October 23

- [x] Re-fetch historical CloudWatch CPU data in bhoomil/us-west-2 without creating resources: two actual samples; receipt saved in `artifacts/cloudwatch-reload-check.json`.
- [x] Show sample count, average, peak, UTC chart and exact rows before AI starts; keep the percentage axis at 0–100.
- [x] Add explicit past-instance selection and recorded demo window, plus a refreshable last-hour window.
- [x] Preserve a matching prior collection on refresh failure; reject stale data when selections change.
- [x] Add clearly labeled saved AWS snapshots retaining original collection timestamps for replay after EC2 deletion.
- [x] Show investigation stages and a link to output; retain diagnostic findings when Bedrock fails.
- [x] Verify actual browser flow: bhoomil account discovery, historical CPU fetch, real Decider selection and Metrics Analyzer findings.
- [x] Pass 78 tests, with 1 optional environment check skipped; check lint and formatting.
- [ ] Successful fresh full AI report in bhoomil remains blocked: Bedrock rejects report-sized calls with daily token quota error. Read-only Service Quotas check reports Amazon Nova Lite daily model-invocation allowance as 0 in us-west-2. Enabling model access alone has not resolved this. No successful report or replacement success video is claimed.

No AWS resources were created during this fix. The earlier cleanup records remain intact.

## New narrated video request — male voice, no subtitles

- [x] Recheck bhoomil/us-west-2 inventory: no active instance remains after cleanup.
- [x] Retry a complete evidence-grounded Bedrock report before provisioning: still rejected for daily token quota (`artifacts/video-new-preflight.json`).
- [x] Implement a clean video renderer with no subtitles, subtitle stream or text overlays; preserve real frame timestamps and verify final decode.
- [x] Prepare male Amazon Polly Stephen narration generation using bhoomil only, with service receipts.
- [x] Generate the male Stephen voice preview and complete eight-chapter narration draft; verify audio decoding and a subtitle-free 1080p encode using existing actual UI captures. This is renderer verification, not a new successful demonstration.
- [ ] Restore Bedrock reporting allowance in bhoomil (user notified; awaiting resolution).
- [ ] Once reporting works, create/check the temporary live demo instance, collect fresh measurements, and verify full agent output before recording.
- [ ] Capture and narrate the complete working flow, inspect playback/audio, then delete and independently verify temporary demo resource cleanup.

The old video has not been relabeled as the new successful demonstration. No new EC2 was provisioned while full reporting remains blocked.


## Ordered diagnosis, verified sample report and final recording — October 23

- [x] Verify actual bhoomil identity privately, region, exact model, bedrock-runtime endpoint and SDK operation.
- [x] Capture complete HTTP 429 / ThrottlingException message and request receipt from the actual SDK call.
- [x] Inspect model-specific and cross-model applied quotas plus model and aggregate CloudWatch token/error metrics; distinguish absent metrics from zero usage.
- [x] Prepare the exact adjustable request route and small proposed allowance without submitting or changing quotas.
- [x] Add explicit sample-report mode using genuine Decider selection and selected diagnostic evidence; label UI, report and JSON provenance. No silent fallback.
- [x] Verify real model decisions and reports for metrics, logs and releases in all four fixture workflows; verify report and provenance in the browser.
- [x] Pass 83 tests, 1 optional check skipped; lint, formatting and dependency consistency checks passed.
- [x] Re-fetch actual historical CloudWatch data while recording: two samples, visible UTC window and collection time; no instance created.
- [x] Exercise Full AI mode on that real evidence in the browser: genuine Strands SDK response is 429; retain diagnostics and report no success.
- [x] Update README, architecture, current/historical verification, narration script and submission checklist with verified repository link.
- [x] Capture all eight final UI scenes and generate male Stephen narration in bhoomil only.
- [x] Export and verify the final 1080p, 30fps video: 149.50 seconds; H.264/AAC; zero subtitle streams and no added text overlays. Full decode, representative visual frames, audio loudness (-16.4 LUFS), browser playback and seeking passed.
- [ ] Publish the reviewed local changes and upload the new video to an accepted public host; add the actual public demo URL.
- [ ] Restore live Bedrock reporting allowance, rerun a real combined report and update the successful-live-demo evidence.
- [ ] Publish the Builder Center article, verify final links, accept entrant terms and submit.

No quota change, new EC2, disk or security group was created for this recording.


## Final temporarily authorized hardik live recording — October 23

- [x] Authenticate hardik privately and inspect model-specific allowances in us-east-1.
- [x] Run genuine Decider/Strands/Bedrock CPU and HTTP-error CLI reports; preserve AWS receipts and validation results.
- [x] Verify the HTTP-error report in the browser with logs, release evidence, citations and next checks.
- [x] Diagnose rejected CPU reports: empty citation lists and missing required information; improve exact-field correction feedback without weakening validation.
- [x] Verify a fresh Nova Pro CPU report in the browser with exact sample counts, unknown impact and low causal confidence.
- [x] Record accepted live reports with male narration and no subtitles; export 158.16 seconds at 1080p/30fps; full decode, eight representative scenes, audio, browser playback and seeking checks passed.
- [x] Pass 84 tests, 1 optional runtime check skipped; lint, format, compile, dependency and focused secret checks passed.
- [x] Stop temporary hardik dashboard; verify port closure and preserved bhoomil default. No infrastructure provisioned or quota changes submitted.
- [x] Audit project-tagged resources in hardik/us-east-1 and us-west-2: zero remaining demo EC2 instances, volumes and security groups.
- [ ] Publish reviewed local changes and upload the latest live video; verify actual public URLs.
- [ ] Publish Builder Center article and complete final submission/entrant approvals.

Latest deliverable: `artifacts/video-hardik-final/OpsPilot-AI-Demo-Male-No-Subtitles.mp4`. Earlier unchecked bhoomil quota-restoration items remain historical blockers for that account; hardik success does not imply bhoomil was fixed.
