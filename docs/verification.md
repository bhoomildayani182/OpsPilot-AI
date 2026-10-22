# Verified execution — October 22, 2026

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

**54 passed, 1 skipped; source statement coverage 94%** (361 statements, 21 missed).
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
- Optional live CloudWatch ingestion is deferred. All shipped scenarios use
  synthetic/supplied telemetry; no production resources were inspected.
