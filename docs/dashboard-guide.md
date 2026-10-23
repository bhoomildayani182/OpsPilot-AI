# How to use and read the OpsPilot dashboard

## Start an investigation

1. Choose **Full AI investigation** in the sidebar for a report generated with
   real Decider 2B and Amazon Bedrock. **View diagnostic findings · no AI** only shows
   observations from checks you select. **AI tool selection only** lets Decider
   choose checks but does not request a Bedrock report.
2. Choose an incident and describe what is going wrong.
3. Check the data counts and open **View the supplied data** to see readable
   measurements, application messages and release events. Included examples are
   synthetic. To read actual CPU measurements, select Live AWS EC2 metrics, connect an account, select an instance and UTC window, then fetch data. See aws-usage-and-cleanup.md.
4. Select **Investigate incident**. Findings appear below the inputs. Changing
   the incident, description, data, checks or mode clears the old findings.

## What the four cards mean

| Card | Meaning | What it does not establish |
| --- | --- | --- |
| Suggested urgency | AI estimate of how serious the symptoms appear. High suggests investigating promptly. | A confirmed outage or measured customer impact. |
| Tool choice certainty | Decider's confidence in which diagnostic check to run first. | The probability that a proposed root cause is correct. |
| Evidence items | Extracted measurement summaries, matching log lines and release events. | The total number of raw input records. |
| Cause confidence | How strongly the evidence supports a possible explanation: low, medium or high. | Whether the symptoms matter; a serious symptom can have an uncertain cause. |

For the CPU example, **89% tool choice certainty** refers to choosing the Metrics
Analyzer. **Low cause confidence** means the actual cause is still uncertain.
**High urgency** is a tentative assessment of the CPU symptom. Those values answer
different questions and can appear together.

The eight supplied measurements cover CPU and memory. The analyzer produces two
summaries, so the evidence count is **2**. `M1 — CPU usage` says **3 of 4 CPU
samples exceed the 90% demo limit**. `M2 — Memory usage` summarizes memory.
A demo limit is an example threshold, not an agreed performance target (SLO)
for your service.

## Read the tabs

- **Findings & next steps:** incident summary, what to check next, possible causes,
  uncertainty and missing information. Possible causes are hypotheses.
- **Evidence explained:** readable observations. M identifies a measurement
  summary; L a log message; D a deployment event. Exact records remain expandable.
- **Why these checks?:** the selected tool, its purpose and the actual selection
  rules. Decider produces scores, not a written reasoning explanation. Detailed
  probabilities and the technical request/response are optional expanders.
- **Download:** save the inputs, decisions, observations and any AI report as JSON.
  Review the data before sharing it.

No infrastructure action is taken. Recommendations are for a person to review.
