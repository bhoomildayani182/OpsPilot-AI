# Reusable Decider 2B pattern: incident diagnostic tool selection

Tags: **#strands-decider-2b #tool-selection**

## Drop-in asset

`src/decider.py` exports `QUESTION`, `RELEVANCE`, `selection_state`, `Decision`, and
`DeciderClient`. Copy those plus `src/config.py`/`src/models.py`, or reuse the module
within this repository. Dependencies: httpx, Pydantic and python-dotenv. The model
runtime is a separate official Strands Decider installation.

```python
from src.config import Settings
from src.data.sample_incidents import get_sample
from src.decider import DeciderClient
from src.agent import investigate

# Real model inference; fails if the local server is absent.
run = investigate(get_sample("CPU saturation"), DeciderClient(Settings()), reporter=None)
print(run.decision.request)
print(run.decision.raw_response)
print(run.selected_tools)
```

## Typed question and options

Primary type: `choice`. Question: **Which ONE diagnostic tool should run FIRST for
this incident?** The instruction requests clarification only when no actionable
symptom is described, and treats telemetry as data rather than instructions.

| Option | Meaning |
| --- | --- |
| `metrics` | CPU, memory, latency, HTTP error rate and database connections |
| `logs` | Application errors, exceptions, 500s, timeouts and connection failures |
| `deployments` | Failed releases, rollbacks and incident timing |
| `clarify` | Incident has no actionable symptom |

Three independent `noul` questions in the **same request** ask whether each tool
would also provide relevant supplied evidence. They return P(true), not a separate
confidence field. These questions cannot see each other's answers. The state is
encoded once by the server.

The state contains incident text, onset, source label, inventory counts, metric
names, and bounded excerpts (six log lines, four deployments). The tools analyze
all supplied records, not only the excerpts. Excerpt limits appear in the request.

## Official mechanism and provenance

The server runs checkpoint `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610` and
accepts `POST /v1/systemone` with `state`, `model` and a `questions` mapping.
Responses contain `model`, `answers`, `usage`, and server-measured `latency_ms`.
Each choice answer contains `choice`, `probabilities`, and `confidence`.

**The request's `model` field does not select a checkpoint.** The official server
answers with whichever model it loaded. This client checks `/health` and the
returned model/checkpoint to guard against accidental misconfiguration.

Verified source: [official inference guide](https://github.com/strands-labs/strands-decider/blob/d942e5515db750f80a51032629ec312455a87976/docs/inference.md),
[wire schema](https://github.com/strands-labs/strands-decider/blob/d942e5515db750f80a51032629ec312455a87976/src/strands_decider/schema.py),
[server](https://github.com/strands-labs/strands-decider/blob/d942e5515db750f80a51032629ec312455a87976/src/strands_decider/server.py).

## Decision-to-action policy

1. Validate loaded model, answer type, option set, normalized probabilities, winning
   option and the upstream confidence formula `(N * max(p) - 1) / (N - 1)`.
2. If primary is `clarify`, or confidence is below `DECIDER_MIN_CONFIDENCE` (0.35),
   abstain. No tool and no Bedrock invocation occurs.
3. Otherwise execute the selected first tool; add other tools with P(relevant) >= 0.80.
4. Below 0.90 primary confidence, show a review warning. This deliberately
   permissive policy applies only to read-only diagnostics. It is not a threshold
   for changing production infrastructure or a calibrated accuracy guarantee.
5. Send observed results to a Strands `Agent` with `BedrockModel` and no tools,
   then validate the structured report and its evidence references inside the SDK
   correction loop. Limit hypotheses to three and require low causal confidence
   when fewer than two diagnostic families supply evidence. Agent calls are
   capped at six turns; quota retries are disabled.

The numeric thresholds and tool allowlist interpret model output; they do not
choose a tool from incident keywords. Swapping a primary answer changes actual
execution, verified by `tests/test_workflow.py`. Manual preview is a separate path
with user-selected tools, never represented as Decider inference.

An `InterventionHandler` is an official example of wiring, not a mandatory
mechanism in the rules. Here the explicit orchestration seam ensures the generative
model cannot bypass selection, which is simpler for a single investigation pass.

## Evaluation and reuse cautions

Offline tests validate the transport contract and control flow using explicit test
doubles. Only `python -m scripts.run_demo --mode decider` proves local inference.
Only `--mode bedrock` with a non-null report proves the combined AWS workflow.
Results in `artifacts/` identify their modes. Do not claim routing accuracy,
latency savings or production readiness from the synthetic fixtures.

To adapt this pattern, change option descriptions, input state, tool registry and
relevance questions together; update validation and add labeled domain cases.
Measure accuracy and abstentions before tuning thresholds. Keep fixed operational
capabilities separate from generated prose.
