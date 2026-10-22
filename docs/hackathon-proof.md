# Hackathon demonstration and evidence

## What is sample data?

The four example incidents contain invented, fixed input records. For CPU saturation,
CPU readings are 88%, 94%, 97%, and 96%; memory readings are 54%, 55%, 56%, and 55%.
They simulate an incident without accessing a real server. Their timestamps are the
simulated incident time, not the time of the AI request.

The original fixtures are synthetic. Live mode separately supports EC2 instance
and UTC time-window selection with actual CloudWatch CPU collection. No application
discovery, log ingestion or server remediation is implemented. Do not describe these examples as real outages
or claim that OpsPilot identified a confirmed production root cause.

## What runs for real?

In **Full AI investigation**, the locally loaded official Strands Decider 2B model
selects the diagnostic checks. The application runs those checks on the input
records, then uses the Strands Agents SDK to call Amazon Bedrock. Bedrock writes
an evidence-cited report. Citation validation and conservative confidence rules
reject unsupported references; they do not independently verify causal claims.

The **Explore sample data · no AI** mode only runs manually selected local checks.
It is useful for learning the interface, but it is not proof of either AI integration.

## Show this in the demo

1. Start the local model and dashboard using the README instructions.
2. Select **Full AI investigation**, then **CPU saturation**.
3. Open **View the supplied data** and explain that the inputs are synthetic.
4. Select **Investigate incident**. Show the selected metrics check, exact sample
   counts and report; distinguish tool-choice certainty from cause confidence.
5. Open **Why these checks?** to show the real Decider request, response and scores.
6. Open **Integration proof** to show Bedrock model, region, UTC call time,
   AWS request IDs, HTTP status and report validation status.
7. Download the investigation JSON. Repeat with **Failed deployment** to show
   that the model can choose a different diagnostic family.

Suggested spoken description: “These incidents are synthetic test inputs. The
local Decider model and Amazon Bedrock calls are real. OpsPilot chooses checks,
extracts evidence and suggests possible explanations and next steps. Live mode separately reads actual CPU measurements for a selected EC2 instance.”

## Evidence files

- `artifacts/hackathon-proof-runs.json`: fresh end-to-end CPU and failed-deployment
  runs, including exact Decider traces, supplied evidence, reports and AWS receipts.
- `artifacts/decider-results.json`: earlier four-scenario real routing verification.
- `artifacts/test-output.txt` and `artifacts/test-results.xml`: actual automated checks.
- `artifacts/hackathon-proof.jpg`: dashboard view of a real run's integration proof.
- `artifacts/hackathon-proof-manifest.json`: SHA-256 file hashes for detecting changes.
- `artifacts/hackathon-proof.zip`: portable collection of the above evidence and this guide.

AWS request IDs are service-response metadata captured by botocore, not independent
certification. HTTP 200 alone can precede a failed streaming response or report
validation; require both saved receipts and a successfully validated report. The
archive and manifest are generated locally and are not signed attestations. No
credentials, authorization headers, raw error messages or full account identities
are intentionally included in these receipts. Review all exports before publishing.

## Repeat the cloud verification

From the project root, with the local model running and an authorized AWS profile:

```sh
.venv/bin/python -m scripts.run_demo --mode bedrock \
  --scenario 'CPU saturation' --scenario 'Failed deployment' \
  --output artifacts/hackathon-proof-runs.json
```

This makes paid Bedrock model calls. A nonzero exit or missing report means the
verification is incomplete. Output is never replaced with a fake successful report.

The official event requires a meaningful Decider 2B + Bedrock implementation,
a public source repository, Builder Center article and public video under three
minutes. Evidence files support a demonstration; they do not replace those
submission requirements or establish eligibility.

Official event: https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon?tab=about

For the subsequent real EC2 verification and cleanup record, see
[ AWS usage and cleanup](aws-usage-and-cleanup.md). The original two-run proof
file remains a synthetic-input verification; live evidence is saved separately.
