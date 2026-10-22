# OpsPilot AI demo recording script — target 2:45

Do not record in preview mode. Before recording, start Decider and Streamlit,
configure a verified Bedrock model, and run both demo scenarios. Use only synthetic
data. Hide terminal/profile details and notifications. No music is needed.

## 0:00–0:20 · Problem and scope

**Screen:** Dashboard hero and synthetic incident selector.

**Say:** “OpsPilot AI investigates DevOps incidents. An engineer provides a symptom
and telemetry. A small Strands Decider 2B model chooses diagnostics, and Amazon
Bedrock turns the observed evidence into a report. Everything is read-only.”

## 0:20–1:10 · CPU investigation

**Screen:** Select Decider 2B + Bedrock, CPU saturation, click Investigate. Include
real waiting time or clearly label any cut. Open Decision trace.

**Say:** “This is synthetic CPU telemetry. The tool decision comes from the real
local Decider model, not a keyword router. Here are its typed question, option
probabilities, loaded checkpoint and measured round-trip time. These numbers are
from this run; they are not a speed comparison against another model.”

**Screen:** Observed evidence, then Report.

**Say:** “The metrics tool calculates the sample statistics. Evidence has stable
IDs. Bedrock receives only the selected diagnostics and cites those IDs. Potential
causes are hypotheses, with uncertainty and further information to collect.”

## 1:10–1:55 · Failed deployment

**Screen:** Select Failed deployment, Investigate, show decision and deployment evidence.

**Say:** “A failed release presents a different diagnostic need. The model makes a
new selection from the same options. The deployment analyzer compares the supplied
event times with incident onset. A nearby release is a correlation, not proof that
it caused an outage. Missing telemetry stays visible.”

## 1:55–2:25 · Guardrails and reuse

**Screen:** Decision trace and reusable pattern documentation.

**Say:** “Low-confidence decisions are flagged; very uncertain routing abstains.
A missing model never becomes a fake AI result. The reporting agent has no tools
that can change infrastructure. The repository includes the typed question, option
set, client, enforced routing seam and a guide another builder can adapt.”

## 2:25–2:45 · Close

**Screen:** Report next steps, export button, then final repository/article links.

**Say:** “OpsPilot makes incident investigation inspectable: why a tool ran, what
it actually observed, and what remains uncertain. The project includes four sample
incidents and automated checks. The code and reusable tool-selection pattern are
open source under Apache 2.0.”

## Recording acceptance checks

- Run the final script aloud and keep the video below 180 seconds; aim for 165.
- Show genuine Decider identity/decision and a real Bedrock report for two incidents.
- If routing abstains or Bedrock fails, fix/re-run before claiming a successful demo.
- Publish to an accepted public host and open the link signed out to verify access.
- Add #strands-decider-2b and #tool-selection to the submission/article.
