# OpsPilot AI

A read-only DevOps incident investigator. **Strands Decider 2B selects diagnostics;
Amazon Bedrock explains their observed evidence through the Strands Agents SDK.**

Pattern: **#strands-decider-2b #tool-selection** · License: Apache-2.0

![Verified labelled sample report with real Decider selection](artifacts/sample-report-dashboard.png)

The dashboard includes four synthetic incidents: CPU saturation, HTTP 500s, failed
deployment, and database timeouts. It shows the typed model decision, probabilities,
selected tools, literal evidence, causal hypotheses and missing information.

## Current verified status — October 23, 2026

**[Watch the final live Bedrock demo — 2:38, male narration, no subtitles](artifacts/video-hardik-final/OpsPilot-AI-Demo-Male-No-Subtitles.mp4).** [Local review player](artifacts/video-hardik-final/review.html). This recording shows accepted live reports for both HTTP errors and CPU measurements.

**Latest live verification:** with the user’s temporary authorization, **hardik / us-east-1** successfully generated fresh CPU and HTTP-error reports through genuine Decider 2B, Strands Agents SDK and `amazon.nova-lite-v1:0`. The dashboard also accepted a new HTTP-error report with L1/L2/D1 citations and AWS HTTP 200 receipts. After two later Nova Lite CPU format failures, a separate Nova Pro CPU check passed; [its exact report and receipts](artifacts/video-hardik-final/nova-pro-check.json) are preserved. Inputs are explicitly synthetic; this is live AI generation, not live EC2 telemetry. Proof is in [the live verification folder](artifacts/video-hardik-final/verified-live-reports.json). The saved default configuration remains bhoomil.

**84 tests passed; 1 optional runtime check skipped.** The real Decider 2B model
selected tools and produced labelled local sample reports for all four incidents.
The Streamlit workflow was also exercised in a real browser. See
[verification](docs/verification.md) and [actual sample runs](artifacts/sample-workflow-verified.json).

Live Bedrock reporting in **bhoomil / us-west-2** is currently blocked. The actual
Strands SDK call to `amazon.nova-lite-v1:0` on `bedrock-runtime` returns HTTP 429,
`ThrottlingException`: “Too many tokens per day, please wait before trying again.”
The model's daily allowance is 0; the separate cross-model daily allowance is
150 million. [Diagnosis and precise request steps](docs/bedrock-diagnosis.md).
No quota increase has been submitted or assumed approved.

Choose **Demo report · real Decider 2B** for a complete, clearly labelled report
without a Bedrock call. It uses real tool selection and current diagnostic evidence,
then a local template; it is not a successful live AI response. **Full AI
investigation** continues to use the genuine Strands Agents SDK / Bedrock provider
and preserves evidence on failure. There is no automatic report substitution.

## Run locally

Python 3.13 is used in this workspace. Create an isolated environment from the
repository root (the folder containing this README):

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp -n .env.example .env
OPSPILOT_AWS_PROFILE=bhoomil AWS_REGION=us-west-2 streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open http://127.0.0.1:8501. **View diagnostic findings · no AI** works without AWS or model
weights. You manually choose tools; this mode does not claim an AI decision or
Bedrock-generated report. Select an incident and press **Investigate incident**.

## Start genuine Strands Decider 2B

Keep its runtime separate from the dashboard dependencies. On Apple silicon:

```bash
python3.13 -m venv .decider-venv
.decider-venv/bin/python -m pip install -r requirements-decider.txt
HF_HOME="$PWD/.cache/huggingface" .decider-venv/bin/strands-decider serve \
  StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 \
  --device mlx --host 127.0.0.1 --port 8099 --strict-window
```

For CPU use `--device cpu`; for a supported NVIDIA environment use the official
[cuda installation guide](https://github.com/strands-labs/strands-decider/blob/d942e5515db750f80a51032629ec312455a87976/docs/inference.md).
The first model start downloads the checkpoint plus approximately 4.5 GB of base
weights. Leave the server running. The runtime is pinned to official commit
`d942e5515db750f80a51032629ec312455a87976` because MLX extras are newer than the
published 0.1.0 package described in upstream documentation.

`STRANDS_DECIDER_URL=http://127.0.0.1:8099` is the default. Only loopback endpoints
are accepted. The upstream server has no authentication; keep it local.

## Configure Bedrock

Use an AWS profile you control with access to a Bedrock text model. Do not paste
access keys into the app or repository. Set these non-secret options in `.env`:

```dotenv
OPSPILOT_AWS_PROFILE=bhoomil
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
```

`OPSPILOT_AWS_PROFILE` takes precedence over an inherited `AWS_PROFILE`, so the
app does not accidentally use a desktop session's expired SSO profile.

`amazon.nova-lite-v1:0` was returned by the Bedrock model catalog in the selected
account. Availability depends on your account and region; the application does not
hardcode that ID. To discover models and check authentication:

```bash
.venv/bin/python -m scripts.check_access --list-models
```

Restart Streamlit after changing `.env`.

Select **Full AI investigation** to run the combined workflow, or **AI tool selection only** to verify routing without generative AWS calls. Synthetic telemetry
is analyzed locally; only the incident and selected observed evidence go to Bedrock.
See [security and least privilege](docs/security.md).

## Reproduce checks and demonstrations

```bash
.venv/bin/python -m pytest -q --cov=src --cov-report=term-missing
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m scripts.run_demo --mode preview --output artifacts/preview-results.json
.venv/bin/python -m scripts.run_demo --mode decider --output artifacts/decider-results.json
.venv/bin/python -m scripts.run_demo --mode bedrock \
  --scenario 'CPU saturation' --scenario 'Failed deployment' \
  --output artifacts/bedrock-results.json
```

The last two commands invoke the real model; the Bedrock command incurs model
usage charges. Test doubles in offline tests verify contracts and error handling,
not live model availability. A run with no generated report is not a completed
Bedrock integration verification. Actual results are recorded in
[verification](docs/verification.md) and [execution checklist](CHECKLIST.md).

## Read the dashboard

See the [plain-language dashboard guide](docs/dashboard-guide.md) for the meaning
of urgency, tool choice certainty, cause confidence and evidence IDs. The UI
separates observations from possible explanations and clears old findings when
you change the inputs.

## How it works

1. Validate bounded, timezone-aware telemetry and label its source.
2. Ask local Decider a typed four-option primary-tool question and three independent
   relevance questions in one HTTP request.
3. Validate checkpoint identity, probability distribution, choice and confidence.
4. Abstain for `clarify` or confidence below 0.35; otherwise execute the primary
   tool and other tools with P(relevant) >= 0.80. Flag primary confidence below 0.90.
5. Generate a Pydantic report with Strands `Agent` / `BedrockModel`, no operational
   tools, and only the selected tools' facts.
6. Reject unknown evidence references. Display observed facts separately from
   generated hypotheses and export the full trace as JSON.

Metric thresholds and deployment time windows are explicit demo heuristics, not
service SLOs or proof of a root cause. Missing logs are not evidence of health.
Evidence-reference checks do not prove semantic correctness. Humans review reports
and approve any operational changes outside this app.

## Project map

- `app.py`: Streamlit dashboard, JSON telemetry editing and export.
- `src/decider.py`: reusable typed decision pattern and validated HTTP client.
- `src/agent.py`: selection-to-execution orchestration seam.
- `src/bedrock_analyzer.py`: real Strands/Bedrock structured reporting.
- `src/tools/`: three deterministic read-only analyzers.
- `src/data/sample_incidents.py`: fixed synthetic fixtures.
- `tests/`: tools, boundaries, model contract, workflow and dashboard checks.
- `docs/architecture.md`: architecture diagram and trust boundaries.
- `docs/decision-pattern.md`: reusable pattern, thresholds and adaptation guide.
- `docs/builder-center-article.md`: article draft for review before publishing.
- `docs/demo-script.md`: timed public-demo recording script.
- `docs/submission-checklist.md`: official requirements and outstanding actions.

## Troubleshooting

- **Decider unavailable:** start the official server and wait for model loading;
  keep the model ID/checkpoint exact. No mocked fallback is used.
- **Token window exceeded:** reduce incident/excerpt size; the server uses strict
  window mode so oversized prompts fail instead of silently losing evidence.
- **AWS authentication expired:** refresh your chosen profile (for SSO, use
  `aws sso login --profile your-profile`).
- **AccessDenied / reporting error:** verify `bedrock:InvokeModel`, model access,
  region and supported tool/structured-output capability. Evidence remains visible.
- **Validation rejection:** inspect your input units/timezones or the exported
  report/decision trace. Never relabel an invalid or failed run as successful.

## Hackathon status

This repository prepares a submission; publication, eligibility verification,
video recording/upload, article publication and final submission remain explicit
review actions. See the checklist for current evidence. No latency savings or
accuracy improvement over an LLM is claimed.

For an honest synthetic-input demonstration and recorded AWS integration evidence,
see [Hackathon proof and demo steps](docs/hackathon-proof.md). The dashboard now
includes an **Integration proof** tab with service receipts for newly generated runs.

## Live AWS data and cleanup

Select **Live AWS EC2 metrics**, choose a profile/region, connect, select an
instance and UTC time window, and fetch real CPU averages. **Full AI investigation**
uses that snapshot with Decider and Bedrock. No memory, application logs or release
events are collected in live mode. The dashboard does not provision infrastructure.
See [AWS usage and cleanup](docs/aws-usage-and-cleanup.md), including the separately
authorized disposable EC2 test and its recorded cleanup status.

CPU counts, average, peak, chart and exact UTC rows appear immediately after
collection, before AI analysis. With no active instance, enter a past instance ID
and a window when it ran (within 14 days), or choose **Saved AWS snapshot** to
inspect the recorded demo without a new AWS request. Saved snapshots retain their
original collection time. The investigation shows its stages and preserves
diagnostic output if Bedrock reporting fails. A Bedrock quota error still requires
the AWS account allowance to be restored; it is not a successful AI report.

## Complete demo with no live reporting quota

1. Start the local Decider server using the command above, and start Streamlit.
2. Choose **Demo report · real Decider 2B** and **Examples or pasted data**.
3. Select **HTTP 500 errors**, inspect its synthetic metrics/logs/release event,
   and press **Investigate incident**. Use **View investigation output**.
4. Review the labelled sample report, citations and next steps. Inspect
   **Evidence explained**, **Why these checks?**, and **Integration proof**.
5. Repeat with **CPU saturation** to see a different genuine tool selection and
   the exact CPU measurements. No AWS request is made in this combination.

Reproduce all four real model decisions and sample reports:

```bash
OPSPILOT_AWS_PROFILE=bhoomil AWS_REGION=us-west-2 .venv/bin/python -m scripts.run_demo --mode sample --output artifacts/sample-workflow-verified.json
```

Explicit live-report verification (makes paid inference calls when allowed):

```bash
OPSPILOT_AWS_PROFILE=bhoomil AWS_REGION=us-west-2 .venv/bin/python -m scripts.run_demo --mode bedrock --scenario 'CPU saturation' --output artifacts/current-bedrock-verification.json
```

The [architecture](docs/architecture.md) explains the genuine SDK path and the
separate sample formatter. [Submission checklist](docs/submission-checklist.md)
tracks the public repository, review recording and still-unpublished submission links.
