"""OpsPilot AI Streamlit dashboard. Run: streamlit run app.py"""

import json

import streamlit as st
from pydantic import ValidationError

from src.agent import TOOLS, investigate, preview
from src.bedrock_analyzer import BedrockAnalyzer
from src.config import Settings
from src.data.sample_incidents import SAMPLES, get_sample
from src.decider import DeciderClient, DeciderError
from src.models import Incident

st.set_page_config(page_title="OpsPilot AI · Incident workspace", page_icon="🧭", layout="wide")
st.markdown(
    """<style>
.block-container {max-width:1320px;padding-top:2rem;}
[data-testid="stMetric"] {background:#151e32;border:1px solid #29354a;padding:16px;border-radius:12px;}
.stButton>button[kind="primary"] {border-radius:8px;font-weight:650;}
h1 {letter-spacing:-1.5px;} .eyebrow {color:#54dec3;font-size:12px;letter-spacing:2px;font-weight:700;}
</style>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🧭 OpsPilot AI")
    st.caption("INCIDENT INVESTIGATION WORKSPACE")
    st.divider()
    mode = st.radio(
        "Investigation mode",
        ["Local evidence preview", "Decider 2B + Bedrock", "Decider 2B + evidence only"],
    )
    st.caption(
        "Preview uses your tool selection and local calculations. Decider modes call the real model; Bedrock mode also generates a report on AWS."
    )
    st.divider()
    st.markdown("**Read-only by design**")
    st.caption(
        "Investigate → review → act manually. OpsPilot cannot restart services, roll back releases, or change infrastructure."
    )
    st.markdown("**Decision pattern**  \n#tool-selection  \n#strands-decider-2b")

st.markdown('<p class="eyebrow">SIGNAL → EVIDENCE → NEXT STEPS</p>', unsafe_allow_html=True)
st.title("Give your incident a clearer direction.")
st.markdown(
    "Choose an incident, inspect the evidence, and trace the decision behind your investigation."
)

try:
    settings = Settings.from_env()
except (ValueError, TypeError):
    st.error("Configuration is invalid. Check .env against .env.example and the README.")
    st.stop()

left, right = st.columns([3, 2], gap="large")
with left:
    scenario = st.selectbox("Incident scenario", list(SAMPLES) + ["Custom incident"])
    base = (
        get_sample(scenario)
        if scenario in SAMPLES
        else Incident(
            title="Describe an infrastructure incident", started_at="2026-10-22T09:01:00Z"
        )
    )
    incident_text = st.text_area(
        "What happened?", value=base.title, height=95, key=f"title_{scenario}", max_chars=2000
    )
    with st.expander("Inspect or edit supplied telemetry", expanded=scenario == "Custom incident"):
        st.caption(
            "Use timezone-aware ISO timestamps. Values are untrusted input; no commands are executed."
        )
        payload = base.model_dump(mode="json")
        payload.pop("title")
        telemetry = st.text_area(
            "Telemetry JSON", json.dumps(payload, indent=2), height=300, key=f"data_{scenario}"
        )
        if scenario == "Custom incident":
            st.caption(
                'For your own data set "data_source" to "user supplied". Do not paste secrets or confidential infrastructure information.'
            )
    manual = list(TOOLS)
    if mode == "Local evidence preview":
        manual = st.multiselect("Tools to run manually", list(TOOLS), default=list(TOOLS))
    run_clicked = st.button("Investigate incident", type="primary", use_container_width=True)
with right:
    st.markdown("#### Investigation path")
    st.markdown(
        "**01 · Route**  \nDecider 2B picks the first diagnostic and scores the relevance of other tools."
    )
    st.markdown(
        "**02 · Observe**  \nAllowlisted analyzers extract facts from the supplied telemetry."
    )
    st.markdown(
        "**03 · Explain**  \nBedrock builds a report with evidence references and explicit uncertainty."
    )
    st.info(
        "Synthetic sample data is included. Preview is available without AWS or model downloads."
    )
    if mode != "Local evidence preview":
        st.caption(f"Local Decider: {settings.decider_url}")
        st.caption(
            f"Bedrock: {settings.bedrock_model or 'model not configured'} · {settings.region}"
        )
        if st.button("Check Decider connection"):
            try:
                health = DeciderClient(settings).health()
                st.success(f"Verified server identity: {health['model']} on {health.get('device')}")
            except DeciderError as exc:
                st.error(str(exc))

if run_clicked:
    st.session_state.pop("investigation", None)
    try:
        if len(telemetry.encode()) > 1_000_000:
            raise ValueError("Telemetry JSON exceeds 1 MB; narrow the time window.")
        data = json.loads(telemetry)
        if not isinstance(data, dict):
            raise ValueError("Telemetry JSON must be an object.")
        incident = Incident.model_validate({**data, "title": incident_text})
        if scenario == "Custom incident" and incident.data_source == "synthetic sample":
            raise ValueError("Custom telemetry must be labeled user supplied or live CloudWatch.")
        with st.spinner("Collecting evidence and tracing the investigation…"):
            if mode == "Local evidence preview":
                run = preview(incident, manual)
            else:
                reporter = BedrockAnalyzer(settings) if mode == "Decider 2B + Bedrock" else None
                run = investigate(incident, DeciderClient(settings), reporter)
        st.session_state["investigation"] = run
    except (json.JSONDecodeError, ValidationError, ValueError, DeciderError) as exc:
        st.error(f"Investigation could not start: {exc}")

run = st.session_state.get("investigation")
if run:
    st.divider()
    st.markdown("### Investigation report")
    st.caption(
        f"Saved run: {run.incident['title']} · {run.mode} · source: {run.incident['data_source']}. Re-run after changing inputs."
    )
    if run.decision is None:
        st.warning(
            "LOCAL EVIDENCE PREVIEW · Tools selected manually. No Decider inference or Bedrock report was generated."
        )
    elif run.decision.caution:
        st.warning(run.decision.caution)
    cards = st.columns(4)
    cards[0].metric("Selected tools", len(run.selected_tools))
    cards[1].metric("Evidence records", sum(len(r.evidence) for r in run.results))
    cards[2].metric(
        "Routing confidence", f"{run.decision.confidence:.1%}" if run.decision else "Manual"
    )
    cards[3].metric("Report severity", run.report.severity.upper() if run.report else "Not run")
    tabs = st.tabs(["Report", "Observed evidence", "Decision trace", "Export"])
    with tabs[0]:
        if run.report_error:
            st.error(run.report_error)
        report = run.report
        if report:
            if run.report_metadata:
                st.caption(
                    f"Report generated via {run.report_metadata['sdk']} · {run.report_metadata['provider']} · {run.report_metadata['model_id']} · {run.report_metadata['region']}"
                )
            st.markdown("#### Incident summary")
            st.write(report.incident_summary)
            st.markdown(
                f"**Severity: {report.severity.upper()}** · {report.severity_rationale.statement}"
            )
            st.caption("Evidence: " + (", ".join(report.severity_rationale.evidence_ids) or "none"))
            st.markdown("#### Potential root causes · hypotheses")
            for finding in report.potential_root_causes:
                st.write(f"• {finding.statement}")
                st.caption("Supporting evidence: " + (", ".join(finding.evidence_ids) or "none"))
            st.markdown(f"**Causal confidence:** {report.confidence}")
            for label, values in [
                ("Uncertainty", report.uncertainty),
                ("Recommended troubleshooting steps", report.recommended_steps),
                ("Additional information required", report.additional_information_required),
            ]:
                st.markdown(f"#### {label}")
                for index, value in enumerate(values, 1):
                    st.write(f"{index}. {value}")
            st.caption(
                "Generated interpretation requires review. Evidence IDs are validated; citation validity does not prove that a hypothesis is true."
            )
        else:
            st.info(
                "No AI report generated for this run. Review the observed evidence and decision trace."
            )
        st.markdown(
            "**Selected tools:** "
            + (", ".join(run.selected_tools) or "none; clarification required")
        )
    with tabs[1]:
        for result in run.results:
            st.markdown(f"#### {result.tool.title()} analyzer")
            if result.evidence:
                st.dataframe(
                    [e.model_dump() for e in result.evidence],
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info("No matching evidence available from this tool.")
            for limitation in result.limitations:
                st.caption("Limitation: " + limitation)
            with st.expander(f"{result.tool.title()} calculations"):
                st.json(result.details)
    with tabs[2]:
        if run.decision:
            st.markdown(
                f"**Model:** {run.decision.model} · **First diagnostic:** {run.decision.primary}"
            )
            st.caption(
                f"Measured client round trip: {run.decision.latency_ms:g} ms · input tokens: {run.decision.input_tokens}. This is not a benchmark against an LLM."
            )
            st.bar_chart(run.decision.probabilities, horizontal=True)
            st.markdown("**Additional-tool relevance P(true)**")
            st.json(run.decision.relevance)
            with st.expander("Exact typed request, response, and loaded checkpoint"):
                st.json(run.decision.to_dict())
        else:
            st.info("No model decision: these tools were selected manually in preview mode.")
    with tabs[3]:
        st.download_button(
            "Download investigation JSON",
            json.dumps(run.to_dict(), indent=2),
            file_name="opspilot-investigation.json",
            mime="application/json",
        )
        st.caption("Exports contain supplied telemetry. Review contents before sharing.")
else:
    st.divider()
    st.caption(
        "READY TO INVESTIGATE · 4 synthetic scenarios · 3 diagnostic tools · Full decision trace"
    )
