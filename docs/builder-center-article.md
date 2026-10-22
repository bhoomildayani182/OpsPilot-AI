# OpsPilot AI: giving incident diagnostic decisions to Strands Decider 2B

**Draft for review — real integration verified; add final public repository and video links before publication.**

Tags: #strands-decider-2b #tool-selection

## Why I built it

During an infrastructure incident, choosing the next diagnostic can be as
important as interpreting its output. CPU saturation suggests metrics; startup
exceptions suggest logs; a failed release makes deployment events relevant.
Investigators need to see both the evidence and the reasoning boundaries.

OpsPilot AI is a read-only incident investigation workspace. The engineer enters
a symptom and supplies metrics, logs and deployment events. Strands Decider 2B
chooses which diagnostics to run. Amazon Bedrock then generates a structured
report through the Strands Agents SDK. The interface exposes the typed decision,
observed evidence, causal hypotheses, uncertainty and next troubleshooting steps.

The included data is synthetic. The four scenarios cover CPU saturation, HTTP
500s after a release, a failed deployment and database timeouts. The project does
not connect to production infrastructure or take corrective actions.

## The meaningful decision

I handed Decider the **tool-selection** decision, before any diagnostic executes.
It receives an incident description, available telemetry counts, metric names and
bounded log/deployment excerpts. A typed `choice` question asks which tool should
run first: metrics, logs, deployments, or clarification.

Three independent yes/no (`noul`) questions ask whether each diagnostic would also
provide relevant supplied evidence. The server answers all four questions in one
request. Decider is a decision model: it returns choices and probabilities rather
than a generated explanation.

The application validates the distribution and model identity before interpreting
the answer. If the primary answer is clarification, or its normalized choice
confidence is below 0.35, the investigation abstains. Otherwise the first selected
tool runs, along with additional tools whose relevance probability is at least
0.80. Primary confidence below 0.90 produces a visible review warning.

These are hand-chosen policies for a read-only prototype, not thresholds for
changing infrastructure. They need domain evaluation before production use.

## Separate facts from interpretation

Each diagnostic produces facts with IDs. Metrics Analyzer computes sample ranges,
means and counts above explicit demonstration thresholds. Log Analyzer preserves
literal matching error lines. Deployment Analyzer reports timing relative to
incident onset, labeling temporal proximity as correlation rather than cause.

Missing data is a limitation. An empty error-log result does not establish health,
and a recent deployment does not establish a root cause.

Bedrock receives only the selected tools' observations. A Strands `Agent` backed by
`BedrockModel` returns a Pydantic report covering severity, evidence references,
possible causes, causal confidence, uncertainty and next steps. The agent has no
operational tools. Report references must resolve to actual observed evidence IDs.
That check prevents fabricated IDs, but does not prove a generated sentence is
entailed by its citation. Human review remains necessary.

## What the interface makes visible

The dashboard separates a report, observed facts, a decision trace and JSON export.
The trace includes the actual typed request and response, checkpoint metadata,
primary probabilities, additional-tool relevance and measured client round-trip
time. Those timings are measurements of a run, not a claimed comparison with a
large language model.

A separate local preview lets someone inspect deterministic diagnostics without
AWS or model downloads. It is explicitly marked as manual evidence preview and
never claims to have used Decider or generated a Bedrock report.

## Verification and lessons

The final offline test run passed 58 tests, with one optional runtime-import
check skipped in the app environment; source statement coverage was 95%. The
real Decider ran all four scenarios. It chose metrics for CPU saturation, logs
plus deployments for HTTP 500s, deployments for the failed release, and logs plus
metrics for database timeouts. All four real requests and responses also passed
the official runtime schema validation in its separate environment.

Two complete scenarios then ran through the Strands SDK and Amazon Bedrock using
Amazon Nova Lite in us-east-1: CPU saturation and failed deployment. Both returned
validated reports with real evidence references and low causal confidence. The
CPU report correctly described three of four samples over 90%, rather than
claiming continuous saturation. The deployment report explicitly stated that
nearby release events do not establish causation.

The first outputs exposed a useful failure: valid JSON and valid evidence IDs
alone do not make an interpretation careful. I moved citation checks into the
SDK's validation-and-correction loop, limited speculative hypotheses, and required
low causal confidence when only one diagnostic family supplies evidence. Manual
review of the regenerated reports remains part of the workflow.

The design makes an important failure boundary concrete: model unavailability is
visible. Decider failure stops routing; Bedrock failure preserves the collected
evidence. Neither is silently replaced with a simulated AI result.

The reusable pattern is intentionally small: typed questions, option descriptions,
a validated local client and one enforced orchestration seam. Another builder can
adapt those parts to a different diagnostic catalog, then add labeled cases to
evaluate selection quality and abstention behavior.

## Try and reuse it

The source includes setup instructions, a separate pinned Decider runtime,
four scenarios, automated checks, architecture documentation and the clearly
labeled reusable tool-selection guide. The code uses Apache-2.0.

- Public repository: **[ADD FINAL VERIFIED PUBLIC REPOSITORY LINK]**
- Public demo video, under three minutes: **[ADD FINAL VERIFIED VIDEO LINK]**
- Reusable pattern: `src/decider.py` and `docs/decision-pattern.md` in that repository.

The next step is a broader labeled evaluation of tool selection, including vague
incidents and irrelevant telemetry. The dashboard now supports explicit read-only EC2 inventory and CloudWatch CPU
ingestion for a selected instance and time window. A separately authorized
disposable instance supplied real test telemetry; the original fixtures remain
clearly labeled synthetic. Application-log ingestion remains future work.

## References

- [Official Strands Decider repository](https://github.com/strands-labs/strands-decider)
- [Official inference/API guide](https://github.com/strands-labs/strands-decider/blob/d942e5515db750f80a51032629ec312455a87976/docs/inference.md)
- [Strands Amazon Bedrock provider](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/amazon-bedrock/)
- [Agent Experience Hackathon](https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon?tab=about)
