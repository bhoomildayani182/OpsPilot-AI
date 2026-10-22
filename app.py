"""OpsPilot AI Streamlit dashboard. Run: streamlit run app.py"""

import hashlib
import json
from html import escape
from pathlib import Path

import streamlit as st
from pydantic import ValidationError

from src.agent import TOOLS, investigate, preview
from src.bedrock_analyzer import BedrockAnalyzer
from src.config import Settings
from src.data.sample_incidents import SAMPLES, get_sample
from src.decider import DeciderClient, DeciderError
from src.models import Incident
from src.presentation import (
    METRIC_LABELS,
    MODE_HELP,
    MODE_LABELS,
    SCENARIO_HELP,
    TOOL_LABELS,
    TOOL_PURPOSES,
    evidence_labels,
    metric_sentence,
    source_label,
)

st.set_page_config(page_title="OpsPilot AI · Incident investigation", page_icon="🧭", layout="wide")
st.markdown(
    f"<style>{Path(__file__).with_name('assets').joinpath('dashboard.css').read_text()}</style>",
    unsafe_allow_html=True,
)


def fact_card(label, text):
    st.markdown(
        f'<div class="op-fact"><div class="op-fact-label">{escape(label)}</div><div class="op-fact-text">{escape(text)}</div></div>',
        unsafe_allow_html=True,
    )


def show_facts(results, exact=False):
    for result in results:
        st.markdown(f"#### {TOOL_LABELS[result.tool]}")
        st.caption(TOOL_PURPOSES[result.tool])
        if result.tool == "metrics":
            for evidence, (name, values) in zip(
                result.evidence, result.details.items(), strict=True
            ):
                fact_card(
                    f"{evidence.id} · {METRIC_LABELS[name][0]}", metric_sentence(name, values)
                )
        else:
            for evidence in result.evidence:
                fact_card(
                    f"{evidence.id} · {'Application log' if result.tool == 'logs' else 'Release event'}",
                    evidence.observation,
                )
        if not result.evidence:
            st.info(
                "No matching observations in the supplied data. This does not prove the system is healthy."
            )
        if result.tool == "deployments" and result.evidence:
            st.caption(
                "A release close to the incident is a possible lead. Its timing alone does not prove it caused the problem."
            )
        if exact:
            with st.expander(f"Exact {result.tool} evidence and limitations"):
                st.json(result.model_dump(mode="json"))
        else:
            st.caption(
                {
                    "metrics": "These are example limits. Your service may use different limits. Measurements alone cannot tell us the cause.",
                    "logs": "Only the supplied messages were checked. The number of matches is not your application's error rate.",
                    "deployments": "Only supplied release events were checked. A nearby release does not prove what caused the incident.",
                }[result.tool]
            )


def cite(ids, labels):
    st.caption(
        "Based on: "
        + (" · ".join(f"{item} — {labels[item]}" for item in ids) or "No observed evidence")
    )


with st.sidebar:
    st.markdown("## 🧭 OpsPilot AI")
    st.caption("Your incident investigation workspace")
    st.divider()
    mode = st.radio("Choose how to investigate", list(MODE_LABELS), format_func=MODE_LABELS.get)
    st.caption(MODE_HELP[mode])
    st.divider()
    st.markdown("**Start here**")
    st.markdown(
        "1. Choose an example or describe your incident.\n2. Check the supplied data.\n3. Run the investigation and review the findings."
    )
    with st.expander("What do these terms mean?"):
        st.markdown(
            "**Metrics:** measurements such as CPU use or response time.\n\n**Logs:** messages written by an application, including errors.\n\n**Deployments:** software releases and rollback events.\n\n**Evidence:** something actually observed in the supplied data.\n\n**Hypothesis:** a possible explanation that still needs checking."
        )
    st.caption(
        "Read-only: OpsPilot analyzes data. It cannot restart servers or change your infrastructure."
    )

try:
    settings = Settings.from_env()
except (ValueError, TypeError):
    st.error("Configuration is invalid. Check .env against .env.example and the README.")
    st.stop()

st.markdown(
    '<div class="op-eyebrow">OPSPILOT AI / INCIDENT WORKSPACE</div>', unsafe_allow_html=True
)
st.title("Investigate an incident")
st.markdown(
    '<p class="op-intro">Understand what the data shows, what might be causing the problem, and what to check next.</p>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.45, 1], gap="large")
with left:
    st.markdown("### 1. Describe the incident")
    scenario = st.selectbox(
        "Choose an example or use your own incident", list(SAMPLES) + ["Custom incident"]
    )
    st.caption(SCENARIO_HELP[scenario])
    base = (
        get_sample(scenario)
        if scenario in SAMPLES
        else Incident(
            title="Describe an infrastructure incident", started_at="2026-10-22T09:01:00Z"
        )
    )
    incident_text = st.text_area(
        "What is going wrong?",
        value=base.title,
        height=110,
        key=f"title_{scenario}",
        max_chars=2000,
        help="Describe the symptom. For example: the application is slow and database requests time out.",
    )
    payload = base.model_dump(mode="json")
    payload.pop("title")
    with st.expander("Edit input data · advanced", expanded=scenario == "Custom incident"):
        st.caption(
            "This JSON contains the measurements, application messages and release history to analyze. The readable preview is alongside it."
        )
        telemetry = st.text_area(
            "Input data (JSON)", json.dumps(payload, indent=2), height=300, key=f"data_{scenario}"
        )
        st.caption(
            'Use timestamps with a timezone. For your own data, set "data_source" to "user supplied". Do not include secrets.'
        )
    manual = list(TOOLS)
    if mode == "Local evidence preview":
        st.markdown("**Checks to run**")
        manual = [
            name
            for name in TOOLS
            if st.checkbox(
                TOOL_LABELS[name], value=True, key=f"manual_{name}", help=TOOL_PURPOSES[name]
            )
        ]
        st.caption(
            "You choose these checks in preview mode. Full AI investigation lets Decider 2B choose them."
        )

# Parse for the readable input preview; errors are presented on submission.
input_incident = None
try:
    if len(telemetry.encode()) > 1_000_000:
        raise ValueError("Input data exceeds 1 MB; narrow the time window.")
    data = json.loads(telemetry)
    if not isinstance(data, dict):
        raise ValueError("Input data must be a JSON object.")
    input_incident = Incident.model_validate({**data, "title": incident_text})
except (json.JSONDecodeError, ValidationError, ValueError) as exc:
    input_error = str(exc)

with right:
    with st.container(border=True):
        st.markdown("### 2. Check the data")
        if input_incident:
            st.markdown(
                f'<span class="op-badge neutral">{escape(source_label(input_incident.data_source))}</span>',
                unsafe_allow_html=True,
            )
            inventory = [
                (len(input_incident.metrics), "measurement", "measurements"),
                (len(input_incident.logs), "log message", "log messages"),
                (len(input_incident.deployments), "release event", "release events"),
            ]
            st.markdown(
                '<div class="op-inventory">'
                + "".join(
                    f"<div><strong>{count}</strong><span>{singular if count == 1 else plural}</span></div>"
                    for count, singular, plural in inventory
                )
                + "</div>",
                unsafe_allow_html=True,
            )
            st.caption(
                "These are the records you supplied. OpsPilot does not fetch live AWS telemetry."
            )
            with st.expander("View the supplied data"):
                st.markdown("**Server measurements**")
                if input_incident.metrics:
                    st.dataframe(
                        [
                            {
                                "Measurement": METRIC_LABELS[m.name][0],
                                "Value": f"{m.value:g}{METRIC_LABELS[m.name][1]}",
                                "Time (with timezone)": m.timestamp.isoformat(timespec="minutes"),
                            }
                            for m in input_incident.metrics
                        ],
                        hide_index=True,
                        width="stretch",
                    )
                else:
                    st.caption("No measurements supplied.")
                st.markdown("**Application messages**")
                for line in input_incident.logs:
                    st.text(
                        f"{line.timestamp.isoformat(timespec='minutes')} [{line.level}] {line.message}"
                    )
                if not input_incident.logs:
                    st.caption("No log messages supplied.")
                st.markdown("**Release history**")
                for event in input_incident.deployments:
                    st.text(
                        f"{event.version} · {event.status} · {event.timestamp.isoformat(timespec='minutes')}\n{event.details}"
                    )
                if not input_incident.deployments:
                    st.caption("No release events supplied.")
        else:
            st.caption(
                "The input data cannot be previewed yet. Correct its JSON or values before investigating."
            )
    with st.expander("How to read the results"):
        st.markdown(
            "**Suggested urgency:** how serious the symptoms appear. It is an AI estimate, not a confirmed outage level.\n\n**Tool choice certainty:** how sure Decider is about which check to run first. It does not tell you whether a cause is correct.\n\n**Cause confidence:** how strongly the available evidence supports a possible cause. Low means more investigation is needed.\n\n**Evidence items:** extracted summaries, error messages and release events. One summary can represent several raw measurements."
        )
    if mode != "Local evidence preview":
        with st.expander("AI connection details"):
            st.caption(f"Decider 2B: {settings.decider_url}")
            st.caption(
                f"Bedrock report model: {settings.bedrock_model or 'not configured'} · {settings.region}"
            )
            if st.button("Check AI tool selector"):
                try:
                    health = DeciderClient(settings).health()
                    st.success(f"Decider is ready: {health['model']}")
                except DeciderError as exc:
                    st.error(str(exc))

run_clicked = st.button("Investigate incident", type="primary", width="content", key="investigate")
st.caption(MODE_HELP[mode])

fingerprint = hashlib.sha256(
    json.dumps([scenario, incident_text, telemetry, mode, manual]).encode()
).hexdigest()
previous = st.session_state.get("input_fingerprint")
if previous != fingerprint:
    st.session_state.pop("investigation", None)
    st.session_state["input_fingerprint"] = fingerprint

if run_clicked:
    st.session_state.pop("investigation", None)
    try:
        if input_incident is None:
            raise ValueError(input_error)
        if scenario == "Custom incident" and input_incident.data_source == "synthetic sample":
            raise ValueError(
                "Label your custom data as user supplied or live CloudWatch, rather than synthetic sample."
            )
        with st.spinner("Checking the supplied data and preparing your findings…"):
            if mode == "Local evidence preview":
                run = preview(input_incident, manual)
            else:
                reporter = BedrockAnalyzer(settings) if mode == "Decider 2B + Bedrock" else None
                run = investigate(input_incident, DeciderClient(settings), reporter)
        st.session_state["investigation"] = run
    except (ValueError, DeciderError) as exc:
        st.error(f"Investigation could not start: {exc}")

run = st.session_state.get("investigation")
if run:
    st.divider()
    st.markdown("## 3. Understand the findings")
    st.write(run.incident["title"])
    st.caption(source_label(run.incident["data_source"]))
    if run.decision is None:
        st.warning(
            "Evidence preview · You selected the checks. No AI tool decision or Bedrock report was generated."
        )
    elif run.decision.needs_clarification:
        st.warning(
            "More information is needed. Decider could not select a check confidently enough. Add a clearer symptom or more data, then try again."
        )
    elif run.decision.confidence < 0.9:
        st.info(
            "Review the tool choice: Decider's certainty is below 90%. The checks are read-only. This score is about choosing a check, not proving a cause."
        )

    summaries = [
        (
            "Suggested urgency",
            run.report.severity.title() if run.report else "Not assessed",
            "AI estimate of seriousness; actual service impact may be unknown.",
            run.report.severity if run.report else "",
        ),
        (
            "Tool choice certainty",
            f"{run.decision.confidence:.0%}" if run.decision else "You chose",
            "Confidence in the first check, not in a root cause.",
            "",
        ),
        (
            "Evidence items",
            str(sum(len(r.evidence) for r in run.results)),
            "Observed summaries, error messages or release events.",
            "",
        ),
        (
            "Cause confidence",
            run.report.confidence.title() if run.report else "Not assessed",
            "How strongly the evidence supports a possible explanation.",
            "",
        ),
    ]
    st.markdown(
        '<div class="op-grid">'
        + "".join(
            f'<div class="op-stat {escape(tone)}"><div class="op-stat-label">{escape(label)}</div><div class="op-stat-value">{escape(value)}</div><div class="op-stat-help">{escape(help_text)}</div></div>'
            for label, value, help_text, tone in summaries
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Checks that ran:** "
        + (
            " · ".join(TOOL_LABELS[name] for name in run.selected_tools)
            or "None — more information needed"
        )
    )
    st.caption(
        "Example incidents use invented measurements, logs and releases. They are not collected from EC2. "
        "Full AI mode uses the real local Decider model and calls Amazon Bedrock with the supplied evidence."
    )
    tabs = st.tabs(
        [
            "Findings & next steps",
            "Evidence explained",
            "Why these checks?",
            "Download",
            "Integration proof",
        ]
    )
    labels = evidence_labels(run.results)
    with tabs[0]:
        if run.report_error:
            st.error(run.report_error)
        report = run.report
        if report:
            st.markdown("### What happened?")
            st.write(report.incident_summary)
            st.markdown("**Why this urgency was suggested**")
            st.write(report.severity_rationale.statement)
            cite(report.severity_rationale.evidence_ids, labels)
            st.markdown("### What to check next")
            for index, step in enumerate(report.recommended_steps, 1):
                st.write(f"{index}. {step}")
            st.caption(
                "These are suggestions for a person to review. OpsPilot has not made any infrastructure changes."
            )
            st.markdown("### Possible explanations")
            st.caption("These are hypotheses, not confirmed root causes.")
            if not report.potential_root_causes:
                st.write("The current evidence does not support a specific explanation yet.")
            for finding in report.potential_root_causes:
                st.write(finding.statement)
                cite(finding.evidence_ids, labels)
            st.markdown("### What is still uncertain?")
            for uncertainty in report.uncertainty:
                st.write(f"• {uncertainty}")
            st.markdown("### More information to collect")
            for item in report.additional_information_required:
                st.write(f"• {item}")
            with st.expander("Report source and validation"):
                st.json(run.report_metadata)
                st.caption(
                    "Evidence IDs are checked. A valid reference does not prove an explanation is correct; review the interpretation."
                )
        else:
            st.markdown("### What the supplied data shows")
            st.caption(
                "No AI report was generated. The observations below come directly from the diagnostic checks; they do not establish a root cause."
            )
            show_facts(run.results)
            if run.decision and run.decision.needs_clarification:
                st.write(
                    "Describe the affected service, the symptom and when it started. Add measurements or error messages if available."
                )
    with tabs[1]:
        st.caption(
            "Facts extracted from the supplied data. M = measurement summary, L = log message, D = deployment event. These IDs connect report statements to their observations."
        )
        st.caption(
            "Demo limits are example thresholds, not your service's agreed performance targets."
        )
        show_facts(run.results, exact=True)
    with tabs[2]:
        if run.decision:
            st.markdown("### Decider 2B chose the first check")
            st.write(f"First choice: **{TOOL_LABELS[run.decision.primary]}**")
            if run.decision.primary in TOOL_PURPOSES:
                st.write(TOOL_PURPOSES[run.decision.primary])
            st.caption(
                "This describes the tool's purpose. Decider returns scores, not a written explanation of its reasoning."
            )
            st.write(
                "The first check runs when choice certainty is at least 35%. Additional checks run when their relevance score reaches 80%. Below 35%, or when clarification is chosen, no checks run."
            )
            st.dataframe(
                [
                    {
                        "Check": TOOL_LABELS[name],
                        "Ran?": "Yes" if name in run.selected_tools else "No",
                        "Relevance": f"{value:.1%}",
                        "Selection rule": "First choice"
                        if name == run.decision.primary
                        else "Additional relevance reached 80%"
                        if name in run.selected_tools
                        else "Not selected",
                    }
                    for name, value in run.decision.relevance.items()
                ],
                hide_index=True,
                width="stretch",
            )
            with st.expander("Compare first-choice probabilities"):
                st.caption(
                    "How Decider distributed its preference across the options; these add up to 100%. They differ from the normalized tool-choice certainty score above. Neither measures root-cause certainty."
                )
                st.bar_chart(
                    {
                        TOOL_LABELS[name]: value * 100
                        for name, value in run.decision.probabilities.items()
                    },
                    horizontal=True,
                )
            with st.expander("Technical decision trace · exact request and response"):
                st.caption(
                    f"Model: {run.decision.model} · measured round trip {run.decision.latency_ms:g} ms. This is not a speed comparison against another model."
                )
                st.json(run.decision.to_dict())
        else:
            st.info(
                "You selected the checks in evidence preview mode. Choose Full AI investigation to let Decider select them and Bedrock generate a report."
            )
    with tabs[3]:
        st.markdown("### Save this investigation")
        st.write(
            "Download the input data, selected checks, evidence and any AI report as one JSON file."
        )
        st.download_button(
            "Download investigation JSON",
            json.dumps(run.to_dict(), indent=2),
            file_name="opspilot-investigation.json",
            mime="application/json",
        )
        st.caption("The file contains your supplied data. Review it before sharing.")
    with tabs[4]:
        st.markdown("### What is real in this run?")
        st.write(f"**Input source:** {source_label(run.incident['data_source'])}")
        if run.decision:
            st.write(f"**Decider inference recorded:** {run.decision.model}")
            st.caption(
                "The exact model request, response and selection scores are saved in the download."
            )
        else:
            st.info("Manual preview: Decider and Bedrock were not called.")
        metadata = run.report_metadata or {}
        receipts = metadata.get("aws_responses", [])
        successful = [r for r in receipts if r.get("request_id") and r.get("http_status") == 200]
        if metadata.get("provider") == "Amazon Bedrock" and successful and run.report:
            st.success(
                "Amazon Bedrock responded and the report passed the application's evidence checks."
            )
        elif metadata:
            st.warning(
                "A successful Bedrock report with an AWS receipt is not verified for this run."
            )
        else:
            st.info("No Bedrock response receipt was recorded for this run.")
        if metadata:
            st.json(metadata)
        st.caption(
            "AWS request IDs help identify service calls; they are not independent certification. "
            "HTTP 200 alone does not prove a finished report. No EC2 discovery or live CloudWatch collection is implemented. "
            "Download the investigation JSON to preserve this run's inputs, decision, evidence, report and receipts."
        )
else:
    st.markdown(
        '<div class="op-empty"><strong>Your findings will appear here.</strong><p>Choose an incident above, check its data, then select <b>Investigate incident</b>. Changing the inputs clears previous findings so you always know which incident you are viewing.</p></div>',
        unsafe_allow_html=True,
    )
