# Current verification — October 23, 2026

## Latest temporarily authorized hardik verification

- Region **us-east-1**, account suffix **5146**, authenticated with hardik; no credential material is stored in these artifacts. Saved defaults remain bhoomil.
- Real Decider → diagnostics → Strands SDK → Nova Lite generated valid CPU and HTTP-error reports in `artifacts/video-hardik-final/verified-live-reports.json`.
- The browser HTTP-error workflow also generated a newly accepted report with L1/L2/D1 citations, three HTTP 200 ConverseStream receipts and actual runtime endpoint metadata.
- Two subsequent browser CPU attempts using Nova Lite exhausted the six-turn structured-report limit. These are rejected attempts, not successes; diagnostic evidence was retained. The rejected proof is preserved alongside the recording.
- One fresh Nova Pro CPU CLI check then passed with validated citations, low causal confidence, unknown severity and AWS HTTP 200 receipts in `nova-pro-check.json`.
- Read-only resource audit found zero non-terminated demo instances, project volumes or project security groups in hardik/us-east-1 and us-west-2. No new EC2, volume, security group or persistent Bedrock Agent was created. On-demand Bedrock and Polly use can be billed; AWS service/audit records are separate from created infrastructure.

- After the citation-feedback fix, the browser accepted a fresh Nova Pro CPU report. The final report gives exact counts/minimum/maximum/mean/window, cites M1/M2, leaves severity unknown and causal confidence low, and makes no claim that memory is healthy. `browser-cpu-success-report.txt` and `browser-cpu-success-proof.txt` preserve this run.
- Final tests: **84 passed, 1 optional check skipped**. Lint, formatting, compilation, dependency consistency and focused secret scan passed. The new regression check confirms that unknown-severity citation failures identify the exact field for model correction.
- Temporary hardik app on port 8502 was stopped and its port closure verified. `.env` still selects bhoomil. See `session-cleanup.json`.

## Final live video verification

The latest review file is `artifacts/video-hardik-final/OpsPilot-AI-Demo-Male-No-Subtitles.mp4`: **158.16 seconds**, 1920×1080, 30fps H.264, 48kHz mono AAC. All eight scenes contain actual timestamped browser captures; footage is edited for time and frames are held where narration outlasts the action. There are zero subtitle streams and no added text overlays. Amazon Polly Stephen provides male generative synthetic narration. Full decode and eight representative scene frames passed inspection; audio measured **-16.4 LUFS**, **-1.4 dBFS true peak**. Capture, narration, checksum and stream manifests accompany the file. Browser playback advanced with sound enabled, no media error and zero text tracks; native seeking reached the accepted HTTP report at 63.28 seconds. See `browser-playback-check.json`.

This video shows successful live Bedrock reports on labelled synthetic data, unlike the earlier sample-mode recording. HTTP uses Nova Lite; CPU uses Nova Pro after the exact citation feedback and output instructions were improved. Rejected attempts are preserved and are not substituted for accepted reports. No quota increase was submitted.

## Earlier bhoomil diagnosis and sample-mode verification

- **83 passed, 1 skipped** in the current automated run; see JUnit, coverage and test output under `artifacts/`.
- Dashboard health at `http://127.0.0.1:8501/_stcore/health` returned `ok`.
- Decider health on port 8099 identified the genuine required checkpoint and MLX backend.
- Four new real Decider runs completed with labelled local sample reports in `artifacts/sample-workflow-verified.json`:
  CPU → metrics; HTTP 500 → logs + deployments; failed deployment → deployments;
  database timeouts → logs + metrics. These selections were model outputs, not fixed application routing.
- Browser verification of HTTP 500 showed the complete report, L1/L2/D1 citations,
  next steps, explicit no-Bedrock labels and real decision metadata.
- Missing evidence produces unknown severity and no fabricated root cause. Invalid
  inputs, Decider abstention/unavailability, changed inputs, and report quota failure
  are covered by tests. A failed live report retains evidence and does not silently
  turn into a sample report.
- Current SDK reporting check in **bhoomil/us-west-2** failed with HTTP 429,
  `ThrottlingException`, exact daily-token message saved in
  `artifacts/bedrock-diagnosis.json`. No successful fresh Bedrock report is claimed for bhoomil.
- Nova Lite is ACTIVE. Its model-specific daily allowance is 0; cross-model daily
  allowance is 150 million. See [exact diagnosis and request steps](bedrock-diagnosis.md).
- Previous demo resources are absent in both used regions; no EC2 was created for
  this sample-mode recording. Read-only historical CloudWatch collection is separate
  from synthetic incident data and from a saved snapshot.

Reproduce the complete demo using the explicit commands in [README](../README.md).
The sample formatter is local and deterministic; all four Decider calls above are
real, while unit/UI tests use test doubles where appropriate.

## Earlier sample-mode video verification

The new review MP4 is `artifacts/video-final-review/OpsPilot-AI-Demo-Male-No-Subtitles.mp4`: **149.50 seconds**, 1920×1080, 30fps H.264 with 48kHz AAC narration. There are **zero subtitle streams**, no burned captions and no added text overlays. The voice is Amazon Polly Stephen, male, generative synthetic narration, with receipts in the narration manifest. All eight scenes use real browser captures, edited for time, with the final frame held where narration outlasts the captured action.

Full decoding completed without errors. Representative frames from every scene were inspected. Audio measured -16.4 LUFS integrated loudness and -1.3 dBFS true peak. Browser playback progressed with sound enabled, no media error, and native seeking reached the report at 63.78 seconds. Capture timestamps, per-scene actual-frame counts, checksum, stream metadata and browser checks are saved alongside the MP4. The recording shows local sample reports and a real historical CloudWatch fetch; its final scene preserves the genuine failed Bedrock response. It does not claim a successful new live AI report.

---

## Historical verification — October 22, 2026

The following earlier results remain historical evidence. They do not override the
current bhoomil quota failure or establish that the new sample report came from Bedrock.



## Environment

- macOS arm64; Python 3.13.12, separate app/model environments.
- Streamlit 1.66.1; Strands Agents SDK 1.62.0; boto3 1.43.117; Pydantic 2.13.5.
- Official Decider source commit `d942e5515db750f80a51032629ec312455a87976`.
- Loaded checkpoint `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`, MLX backend.
- Bedrock model `amazon.nova-lite-v1:0`, `us-east-1`, user-approved AWS test profile.
- `pip check`: no broken application requirements.
- Exact environment snapshots: `requirements-lock.txt` and
  `requirements-decider-lock-macos-arm64.txt` (the latter is platform-specific).

## Automated checks

**71 passed, 1 skipped.** See the current source coverage in `artifacts/coverage.json`.
Actual output: `artifacts/test-output.txt`; JUnit: `artifacts/test-results.xml`;
coverage data: `artifacts/coverage.json`.

The skipped check imports the optional official Decider package inside the app
venv. The runtime is intentionally installed separately. All four *real* requests
and responses were separately validated against `strands_decider.schema` in the
model environment, so protocol verification was performed despite that skip.

Tests cover all sample inputs, exact calculations, missing data, invalid numeric
values and timezones, allowlisting, malformed/wrong-model responses, confidence
abstention, no fabricated fallback, citation feedback, conservative causal
confidence, quota errors, profile precedence and Streamlit interactions.

Ruff lint and format checks passed. Python compilation and dependency consistency
checks passed. Offline tests use explicit test doubles and do not prove inference.
The real runs below are separate evidence.

## Genuine Decider inference: four scenarios

| Scenario | First tool | Actual selected tools | Normalized choice confidence | Client ms |
| --- | --- | --- | --- | --- |
| CPU saturation | metrics | metrics | 0.8896 | 2484.00 |
| HTTP 500 errors | logs | logs, deployments | 0.4737 | 873.35 |
| Failed deployment | deployments | deployments | 0.5240 | 855.61 |
| Database timeouts | logs | logs, metrics | 0.4597 | 862.87 |

The first request includes cold/warm-up effects. These are client round-trip
measurements on this Mac, not a latency benchmark or a cost/accuracy comparison
against an LLM. Confidence measures routing concentration, not root-cause certainty.
All four primary decisions were below the 0.90 review-warning threshold.

Evidence: `artifacts/decider-results.json` includes exact typed requests, raw
server responses, loaded checkpoint metadata and observed diagnostic output.
The source of every supplied record is explicitly `synthetic sample`.

## Genuine Strands + Bedrock end-to-end verification

Both scenarios executed Decider selection -> selected local tools -> Strands
`Agent` / `BedrockModel` -> real Amazon Bedrock -> structured report validation.

| Scenario | Severity (generated, tentative) | Causal confidence | Report ms | Status |
| --- | --- | --- | --- | --- |
| CPU saturation | high | low | 12076.06 | Validated |
| Failed deployment | medium | low | 8428.84 | Validated |

Evidence: `artifacts/bedrock-results.json`. Each report has provider/model/region
metadata. No report was substituted with deterministic text or test-double output.

Manual content review confirmed the CPU report correctly says **3 of 4 samples**
exceeded 90%, with mean 93.75%; it treats workload/process causes as possibilities.
The deployment report cites the failed release and rollback events, explicitly
says temporal proximity does not establish causation, and requests missing logs
and impact information. Both have low causal confidence. Operational changes are
recommendations for human review; no infrastructure action was taken.

Early generated outputs omitted citations and overstated continuity/causation.
The final implementation puts grounding checks inside Strands' output-validation
loop, caps hypotheses at three and requires low causal confidence with evidence
from fewer than two diagnostic families. The successful artifacts above were
regenerated after those fixes. Citation existence still does not prove semantic
entailment; human review remains necessary.

The first AWS account tested returned a daily-token-quota error. A different
user-approved profile allowed the real integration test. The app reports that
quota error explicitly and disables automatic quota retries.

## Dashboard

The Streamlit server runs at `http://127.0.0.1:8501`; Decider at port 8099.
Browser checks exercised actual CPU and failed-deployment routing. AppTest also
verified both sample previews, input rejection and unavailable-model handling.
Screenshots in `artifacts/` record the actual UI, rather than a design mockup.

## Remaining external actions

- Review and publish the public repository under Apache-2.0.
- Record and upload the public demo video; target script is 2:45, under 3 minutes.
- Review/publish the Builder Center article, fill final links, register and submit.
- Entrant confirms eligibility and terms. No registration or submission is claimed.
- Live mode now reads actual EC2 inventory and CPU measurements. The four original
  fixtures remain synthetic. A separately authorized disposable EC2 was used; no
  production workload was inspected.

## Dashboard clarity and CSS review

The revised UI explains all four summary cards, uses readable evidence names,
shows supplied data without requiring JSON knowledge, and keeps model internals
in optional expanders. A new state check clears results when inputs change.

Browser verification covered 1280-pixel desktop and 390-pixel mobile widths.
Measured page width matched the viewport at both widths; all four result cards
fit within their available width. Mobile controls use labeled checkboxes, with
no clipped multiselect chips. Measurements: `artifacts/dashboard-layout-checks.json`;
mobile screenshot: `artifacts/dashboard-mobile.jpg`. The temporary viewport was reset.

A fresh real CPU investigation through the revised dashboard returned a Bedrock
report, 89% tool-choice certainty, high suggested urgency and low causal
confidence. `artifacts/dashboard-report.jpg` shows the actual result. The JSON
was downloaded through the UI and retained as `artifacts/dashboard-ai-run.json`.
The report-view test also uses explicitly recorded integration data to check
rendering without additional AWS calls. Those offline tests do not claim new inference.

## Fresh hackathon evidence

Two additional end-to-end runs succeeded using synthetic CPU and failed-deployment
inputs. `artifacts/hackathon-proof-runs.json` contains real Decider traces and
validated Bedrock reports, with four and two AWS ConverseStream response receipts
respectively. Receipts include UTC times, request IDs and HTTP status, excluding
headers and raw errors. Request receipts are corroborating metadata, not independent
attestation or proof of production telemetry. See [demo guide](hackathon-proof.md).

An earlier dashboard error cannot be diagnosed retrospectively from its generic
message. Fresh authorized-profile calls succeeded; new failures retain safe receipt
metadata and exception type where available.

A subsequent real dashboard run received four AWS HTTP 200 responses but failed
Pydantic output validation. It was rejected without showing a report. This confirms
why receipts alone are insufficient; report generation is not guaranteed on every
attempt. Validation failures now have a specific user-facing message.

## Real EC2 data and cleanup verification

The user subsequently authorized live ingestion and a disposable EC2 demonstration
in the bhoomil profile. Real CloudWatch CPU data was fetched from that instance;
Decider selected metrics and Bedrock (hardik profile) returned a validated report.
The browser independently exercised profile, instance and UTC window selection,
actual collection, correct Live AWS labeling and full reporting.
`artifacts/live-aws-investigation.json`, `live-aws-selection.jpg`, and
`live-aws-proof.jpg` preserve the real run and UI.

The first sample was low CPU (approximately 0.0626%), not a production outage.
It cannot establish a trend. No memory, logs or deployment events were collected.
The bounded temporary shell workload did not imply an application incident.

The temporary instance was then terminated. Independent reads verified its exact
state as terminated and returned NotFound for its recorded root disk and dedicated
security group. `artifacts/ec2-demo-resource.json` records complete cleanup.
Existing network resources were retained.

The earlier missing report was reproduced as `structured_output=None` after four
model turns, rather than evidence of broken AWS credentials. The revised prompt
requests the structured tool directly with allowed evidence IDs and causal
confidence constraints, permits at most six turns, and explicitly rejects missing
output. Three fresh real CPU report tests all passed in one/two Bedrock calls;
this is observed improvement, not a guarantee that every model response will pass.
Results: `artifacts/report-diagnosis.json` and `artifacts/report-fix-verification.json`.
