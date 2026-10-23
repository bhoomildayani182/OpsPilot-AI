# Final live demo narration — October 23, 2026

Male voice: Amazon Polly Stephen (generative synthetic narration). No subtitles or added text overlays. Actual browser footage edited for time. Synthetic incident inputs; genuine local Decider and live Bedrock reporting in temporarily authorized hardik/us-east-1.

## 01-introduction

OpsPilot helps engineers investigate incidents using evidence, rather than guessing from an alert. This demonstration uses the authorized hardik AWS account in US East one. Both the local Decider two B model and Amazon Bedrock are real. The example incident data is synthetic and clearly labelled.

## 02-input-data

Here is a checkout application returning HTTP five hundred errors after a release. We provide example measurements, two application log messages, and a release event. OpsPilot shows what data is available before the investigation. These records were supplied for the demonstration; they were not discovered on a production server.

## 03-investigation

I start a full AI investigation. Strands Decider two B chooses the diagnostic tools locally. For this incident, it selects the log and deployment analyzers. Those read-only checks extract observed evidence. The Strands Agents SDK then sends the selected evidence to Amazon Bedrock to generate a report.

## 04-live-report

The completed output is now visible. This is a newly generated Bedrock report, not a local sample report. It explains the observed exception and release event, cites their evidence identifiers, and recommends next checks. Possible explanations remain hypotheses. The report also states uncertainty and the information still needed to establish service impact and a cause.

## 05-evidence-and-selection

The evidence view lets us inspect the exact observations behind the report. The decision view shows which checks Decider selected and their relevance scores. Tool choice certainty describes that routing decision. It does not measure whether a possible root cause is correct.

## 06-integration-proof

The integration proof identifies the actual Decider model, the hardik reporting profile, and the regional Bedrock endpoint. AWS response receipts and successful report validation are recorded separately. Together with the exported investigation, these let a reviewer inspect the real calls and the evidence used by the agent.

## 07-cpu-investigation

A CPU example leads to a different tool choice: the metrics analyzer. The dashboard displays the actual supplied values, average, peak, and timestamps. Three of four CPU samples exceed the example threshold. Bedrock explains the selected evidence while keeping causal confidence low; measurements alone cannot identify the process responsible.

## 08-boundaries

OpsPilot is an investigation assistant. It does not restart servers or apply infrastructure changes. The inputs can be supplied by a user, collected through the read-only CloudWatch CPU connector, or replayed from a labelled snapshot. This recording created no EC2 instance or persistent Bedrock agent. The temporary hardik session is stopped after verification.
