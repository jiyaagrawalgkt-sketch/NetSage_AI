import html
import os
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Make the project root importable when running: streamlit run src/app.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import diagnose_case, load_cases

ROOT = PROJECT_ROOT
AUDIT_FILE = ROOT / "docs" / "model_audit_log.md"

st.set_page_config(
    page_title="NetSage AI • Network Operations Center",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit theme is more reliable than prefers-color-scheme here.
# The old CSS used @media (prefers-color-scheme: dark), which can make
# text light while the Streamlit app itself is still using a light theme.
try:
    DARK_MODE = str(st.get_option("theme.base") or "light").lower() == "dark"
except Exception:
    DARK_MODE = False

if DARK_MODE:
    APP_BG = "#070d1a"
    CARD_BG = "#0f172a"
    CARD_BORDER = "#263449"
    TEXT = "#f8fafc"
    TEXT_SECONDARY = "#cbd5e1"
    TEXT_MUTED = "#94a3b8"
    NAV_BG = "#0b1220"
    NAV_ACTIVE_BG = "#1e1b4b"
    NAV_ACTIVE = "#a5b4fc"
    CODE_BG = "#0b1220"
    INFO_BG = "#101d33"
else:
    APP_BG = "#f7f8fc"
    CARD_BG = "#ffffff"
    CARD_BORDER = "#e2e8f0"
    TEXT = "#0f172a"
    TEXT_SECONDARY = "#334155"
    TEXT_MUTED = "#64748b"
    NAV_BG = "rgba(255,255,255,.90)"
    NAV_ACTIVE_BG = "#eef2ff"
    NAV_ACTIVE = "#4338ca"
    CODE_BG = "#f8fafc"
    INFO_BG = "#eff6ff"

# -----------------------------
# Theme / styling
# -----------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

[data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(circle at 15% 5%, rgba(99,102,241,.10), transparent 30%),
        radial-gradient(circle at 90% 15%, rgba(6,182,212,.08), transparent 28%),
        {APP_BG};
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
}}
[data-testid="stSidebar"] * {{ color: #e5e7eb !important; }}
[data-testid="stSidebar"] .stSelectbox label {{ color: #cbd5e1 !important; }}
[data-testid="stSidebar"] .stButton button {{
    background: linear-gradient(90deg, #6366f1, #06b6d4);
    border: 0;
    color: white !important;
    font-weight: 700;
}}

.hero {{
    padding: 28px 30px;
    border-radius: 24px;
    color: white;
    background: linear-gradient(135deg, #111827 0%, #1e1b4b 52%, #0e7490 100%);
    box-shadow: 0 18px 45px rgba(15,23,42,.18);
    margin-bottom: 22px;
}}
.hero .eyebrow {{ color: #67e8f9; font-size: 13px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; }}
.hero h1 {{
    margin: 7px 0 5px;
    font-size: 38px;
    letter-spacing: -1.4px;
    color: #ffffff !important;
    opacity: 1 !important;
    visibility: visible !important;
}}

.hero h1 span {{
    color: #67e8f9 !important;
    opacity: 1 !important;
    visibility: visible !important;
}}
.hero p {{ margin: 0; color: #dbeafe; font-size: 15px; }}
.pill {{
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 13px;
    margin-right: 7px;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.16);
}}

.section-title {{ font-size: 22px; font-weight: 800; color: {TEXT} !important; margin: 8px 0 12px; }}
.mini-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 18px;
    padding: 17px 18px;
    box-shadow: 0 8px 24px rgba(15,23,42,.06);
}}
.mini-label {{ color: {TEXT_MUTED}; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .7px; }}
.mini-value {{ color: {TEXT}; font-size: 24px; font-weight: 800; margin-top: 4px; }}
.mini-sub {{ color: {TEXT_MUTED}; font-size: 12px; margin-top: 3px; }}

.case-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 28px rgba(15,23,42,.06);
    margin-bottom: 16px;
}}

.case-id {{ color: #6366f1; font-size: 12px; font-weight: 800; letter-spacing: 1px; }}
.case-title {{ color: {TEXT} !important; font-size: 22px; font-weight: 800; margin-top: 4px; }}
.case-card.selected {{
    background: #e0efff !important;
    border: 2px solid #2563eb !important;
    box-shadow: 0 10px 30px rgba(37, 99, 235, 0.20) !important;
}}

.case-card.selected .case-id {{
    color: #1d4ed8 !important;
    opacity: 1 !important;
}}

.case-card.selected .case-title {{
    color: #0f172a !important;
    opacity: 1 !important;
}}
.status-good {{ color:#047857; background:#ecfdf5; border:1px solid #a7f3d0; padding:8px 12px; border-radius:12px; font-weight:700; }}
.status-warn {{ color:#b45309; background:#fffbeb; border:1px solid #fde68a; padding:8px 12px; border-radius:12px; font-weight:700; }}
.status-bad {{ color:#b91c1c; background:#fef2f2; border:1px solid #fecaca; padding:8px 12px; border-radius:12px; font-weight:700; }}

.workflow {{ display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 18px; }}
.step {{ background:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:14px; padding:9px 12px; font-size:12px; font-weight:700; color:{TEXT_SECONDARY}; }}
.step.active {{ border-color:#818cf8; background:#eef2ff; color:#4338ca; }}

div[data-testid="stMetric"] {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    padding: 14px 16px;
    border-radius: 16px;
    box-shadow: 0 7px 20px rgba(15,23,42,.05);
}}
[data-testid="stMetricLabel"] {{ color: {TEXT_SECONDARY} !important; }}
[data-testid="stMetricValue"] {{ color: {TEXT} !important; }}
[data-testid="stMetricDelta"] {{ color: {TEXT_SECONDARY} !important; }}

/* Navigation: never rely on browser prefers-color-scheme. */
.nav-wrap {{
    background: {NAV_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 14px;
    padding: 4px;
    margin: 8px 0 20px;
}}
.nav-wrap [role="radiogroup"] {{ gap: 4px; }}
.nav-wrap [role="radio"] {{
    color: {TEXT_SECONDARY} !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}}
.nav-wrap [role="radio"] p {{
    color: {TEXT_SECONDARY} !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}}
.nav-wrap [role="radio"][aria-checked="true"] {{
    color: {NAV_ACTIVE} !important;
    background: {NAV_ACTIVE_BG} !important;
    border-radius: 10px;
}}
.nav-wrap [role="radio"][aria-checked="true"] p {{ color: {NAV_ACTIVE} !important; }}

/* Full diagnostic cards */
.diagnostic-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 18px;
    padding: 20px;
    min-height: 145px;
    box-shadow: 0 8px 24px rgba(15,23,42,.07);
    overflow: visible;
}}
.diagnostic-label {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 10px;
}}
.root-cause-text {{
    color: {TEXT} !important;
    font-size: 20px;
    font-weight: 700;
    line-height: 1.45;
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: normal;
}}
.diagnostic-value {{
    color: {TEXT} !important;
    font-size: 30px;
    font-weight: 800;
    line-height: 1.2;
}}
.confidence-card {{ border-color: #86efac; }}
.confidence-card .diagnostic-value {{ color: #047857 !important; }}

.result-box {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
}}
.result-box-title {{ color: {TEXT} !important; font-size: 17px; font-weight: 800; margin-bottom: 8px; }}
.result-box-text {{ color: {TEXT_SECONDARY} !important; font-size: 15px; line-height: 1.6; }}

/* Normal Streamlit text: explicit colors prevent faded text. */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] label {{
    color: {TEXT} !important;
}}
/* Make all headings and normal text clearly visible */
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6 {{
    color: {TEXT} !important;
    opacity: 1 !important;
}}

.hero h1 {{
    color: #ffffff !important;
    opacity: 1 !important;
}}

.hero p {{
    color: #dbeafe !important;
    opacity: 1 !important;
}}

.hero .eyebrow {{
    color: #67e8f9 !important;
    opacity: 1 !important;
}}

/* ================================
   CASE SUMMARY CARDS
   ================================ */

.summary-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 18px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 8px 24px rgba(15,23,42,.07);
    overflow: visible;
}}

.summary-label {{
    color: {TEXT_SECONDARY} !important;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
}}

.summary-value {{
    color: {TEXT} !important;
    font-size: 27px;
    font-weight: 800;
    line-height: 1.25;

    /* IMPORTANT: do not cut text */
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere;
    word-break: normal;
}}

.severity-value {{
    color: #dc2626 !important;
}}


/* Streamlit info/warning boxes */
[data-testid="stAlert"],
[data-testid="stAlert"] * {{
    color: {TEXT} !important;
    opacity: 1 !important;
}}

[data-testid="stAlert"] p {{
    color: {TEXT} !important;
    opacity: 1 !important;
}}
[data-testid="stCaptionContainer"] {{ color: {TEXT_MUTED} !important; }}

/* Code blocks */
[data-testid="stCodeBlock"] {{
    background: {CODE_BG} !important;
    border: 1px solid {CARD_BORDER} !important;
    border-radius: 12px !important;
}}

/* Evidence cards: readable text with no clipping */
.evidence-card {{
    background: {INFO_BG} !important;
    border: 1px solid #93c5fd;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
    overflow: visible !important;
}}
.evidence-text {{
    color: #0f172a !important;
    font-size: 15px;
    font-weight: 600;
    line-height: 1.65;
    white-space: normal !important;
    overflow-wrap: anywhere;
}}
.evidence-card pre {{
    color: #0f172a !important;
    background: transparent !important;
    border: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    font-family: "Courier New", monospace;
    font-size: 14px;
    line-height: 1.65;
    white-space: pre-wrap !important;
    overflow: visible !important;
    overflow-wrap: anywhere;
}}
.subheading {{
    color: #2563eb !important;
    font-size: 14px;
    font-weight: 800;
    margin-top: 12px;
    margin-bottom: 5px;
}}
.normal-text {{
    color: {TEXT} !important;
    font-size: 15px;
    line-height: 1.65;
    margin-bottom: 12px;
    overflow-wrap: anywhere;
}}

/* Streamlit info boxes */
[data-testid="stAlert"] {{
    color: {TEXT} !important;
}}


/* -------------------------------------------------
   Final readability + layout fixes
   ------------------------------------------------- */

/* Sidebar: do not fade descriptive text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
    color: #e5e7eb !important;
    opacity: 1 !important;
}}

[data-testid="stSidebar"] .mini-label {{
    color: #cbd5e1 !important;
    opacity: 1 !important;
}}

[data-testid="stSidebar"] .mini-sub {{
    color: #cbd5e1 !important;
    opacity: 1 !important;
}}

/* Main captions should remain readable */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {{
    color: {TEXT_SECONDARY} !important;
    opacity: 1 !important;
}}

/* Make all result text solid and readable */
.result-box-text,
.result-box-title,
.finding-text,
.fix-step,
.verification-box {{
    opacity: 1 !important;
}}

.result-box-text {{
    color: {TEXT} !important;
}}

.risk-text {{
    font-size: 16px;
    font-weight: 800;
    color: {TEXT} !important;
}}

.finding-text {{
    color: {TEXT} !important;
    font-size: 15px;
    line-height: 1.65;
    margin: 7px 0;
}}

.ready-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 18px;
    padding: 22px;
    margin: 18px 0;
}}

.ready-title {{
    color: {TEXT} !important;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 6px;
}}

.ready-text {{
    color: {TEXT_SECONDARY} !important;
    font-size: 15px;
    line-height: 1.6;
}}

.fix-step {{
    color: {TEXT} !important;
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 8px;
    line-height: 1.55;
}}

.verification-box {{
    color: {TEXT} !important;
    background: {INFO_BG};
    border: 1px solid #93c5fd;
    border-radius: 12px;
    padding: 13px;
    line-height: 1.55;
}}

.root-card {{
    min-height: 145px;
}}

.root-cause-text {{
    max-width: none !important;
    width: 100% !important;
}}

.diagnostic-card,
.result-box,
.evidence-card,
.summary-card {{
    opacity: 1 !important;
}}

@media (max-width: 900px) {{
    .diagnostic-card {{
        min-height: auto;
    }}
}}

footer {{ visibility: hidden; }}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# State / data
# -----------------------------
st.session_state.setdefault("diagnosis", None)
st.session_state.setdefault("selected_case", None)
st.session_state.setdefault("decision", None)
st.session_state.setdefault("active_tab", "🏠 Overview")


@st.cache_data
def get_cases():
    return load_cases()


cases_df = get_cases()


def read_audit():
    cols = ["timestamp", "case", "decision", "root_cause", "confidence", "human_edit", "reason"]
    if not AUDIT_FILE.exists():
        return pd.DataFrame(columns=cols)

    rows = []
    for line in AUDIT_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and not line.startswith("|---"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 7 and parts[0] != "Timestamp":
                rows.append(parts[:7])
    return pd.DataFrame(rows, columns=cols)


def append_audit(case, decision, diagnosis, edited_command="", reason=""):
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_FILE.exists():
        AUDIT_FILE.write_text(
            "# NetSage AI Model Audit Log\n\n"
            "| Timestamp | Case | Decision | AI Root Cause | Confidence | Human Edit | Reason |\n"
            "|---|---|---|---|---:|---|---|\n",
            encoding="utf-8",
        )

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    root = str(diagnosis.get("root_cause", "")).replace("|", "\\|")
    reason = str(reason).replace("|", "\\|").replace("\n", " ")
    edited = str(edited_command).replace("|", "\\|").replace("\n", "<br>")
    line = (
        f"| {ts} | {case['case_id']} | {decision} | {root} | "
        f"{diagnosis.get('confidence', 0)} | {edited} | {reason} |\n"
    )
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


def confidence_value(value):
    try:
        v = float(value)
        return v * 100 if v <= 1 else v
    except (TypeError, ValueError):
        return 0.0


def safe_text(value):
    """Escape dynamic values before placing them into HTML."""
    return html.escape(str(value if value is not None else ""))


# -----------------------------
# Current case
# -----------------------------
audit = read_audit()
case_ids = cases_df["case_id"].tolist()

if not case_ids:
    st.error("No troubleshooting cases were found in data/cases.csv.")
    st.stop()

stored_case = st.session_state.get("selected_case")
selected_id = stored_case if stored_case in case_ids else case_ids[0]

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🌐 NetSage AI")
    st.caption("Network Operations Console")
    st.divider()

    selected_id = st.selectbox(
        "Troubleshooting Case",
        case_ids,
        index=case_ids.index(selected_id),
        format_func=lambda x: (
            f"{x}  •  "
            f"{cases_df.loc[cases_df.case_id == x, 'concept_tag'].iloc[0]}"
        ),
        key="case_selector",
    )
    selected = cases_df[cases_df["case_id"] == selected_id].iloc[0].to_dict()

    # Selecting a different case clears the old result.
    previous_case = st.session_state.get("selected_case")
    if previous_case is not None and previous_case != selected_id:
        st.session_state.diagnosis = None
        st.session_state.decision = None
        st.session_state.active_tab = "🏠 Overview"
    st.session_state.selected_case = selected_id

    severity = safe_text(selected.get("severity", "Unknown"))
    osi = safe_text(selected.get("osi_layer", "Unknown"))
    concept = safe_text(selected.get("concept_tag", "Unknown"))

    st.markdown(
        f"""
        <div class="mini-card" style="background:#172033;border-color:#334155;">
            <div class="mini-label" style="color:#94a3b8;">Current severity</div>
            <div class="mini-value" style="color:white;">{severity}</div>
            <div class="mini-sub" style="color:#94a3b8;">OSI {osi} • {concept}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔍  Run AI Diagnosis", type="primary", width="stretch"):
        with st.spinner("Analyzing evidence…"):
            result = diagnose_case(selected)
            st.session_state.diagnosis = result
            st.session_state.selected_case = selected_id
            st.session_state.decision = None
            st.session_state.active_tab = "🧠 Diagnose"
        st.toast("Diagnosis ready — opening results", icon="✅")
        st.rerun()

    st.divider()
    st.markdown("### Safety Gate")
    st.caption(
        "AI recommendations are advisory. Approve, edit, or reject every remediation before lab deployment."
    )
    st.markdown(
        '<div class="status-good">● Simulation mode • No device connection</div>',
        unsafe_allow_html=True,
    )

# -----------------------------
# Hero
# -----------------------------
hero_provider = "Gemini" if os.getenv("GEMINI_API_KEY", "").strip() else "AI / fallback"
st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">AI-assisted network troubleshooting</div>
      <h1>NetSage AI <span style="font-size:22px;color:#67e8f9;">NOC Console</span></h1>
      <p>Diagnose Packet Tracer failures with deterministic checks, evidence-backed AI reasoning, and mandatory human approval.</p>
      <span class="pill">30 lab cases</span>
      <span class="pill">Hybrid diagnostics</span>
      <span class="pill">Human-in-the-loop</span>
      <span class="pill">Audit ready</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# KPI row
# -----------------------------
k1, k2, k3, k4, k5 = st.columns(5)
audit_count = len(audit)
accepted = int((audit["decision"] == "ACCEPTED").sum()) if audit_count else 0
rejected = int((audit["decision"] == "REJECTED").sum()) if audit_count else 0
agreement = round(100 * accepted / audit_count, 1) if audit_count else 0

k1.metric("Lab Cases", len(cases_df), "Coverage")
k2.metric("Issue Types", cases_df["concept_tag"].nunique(), "Network themes")
k3.metric("Audited Decisions", audit_count, "Human reviewed")
k4.metric("AI Agreement", f"{agreement}%", "Accepted / reviewed" if audit_count else "No decisions yet")
k5.metric("Rejected", rejected, "False-positive feedback")

# -----------------------------
# Navigation
# -----------------------------
st.markdown('<div class="nav-wrap">', unsafe_allow_html=True)
active_tab = st.radio(
    "Navigation",
    ["🏠 Overview", "🧠 Diagnose", "📊 Analytics", "🛡️ Audit & Safety"],
    key="active_tab",
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Overview
# -----------------------------
if active_tab == "🏠 Overview":
    st.markdown('<div class="section-title">Operations Overview</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.35, 1])
    with c1:
        concept_counts = cases_df["concept_tag"].value_counts().reset_index()
        concept_counts.columns = ["Issue Type", "Cases"]
        fig = px.bar(
            concept_counts,
            x="Cases",
            y="Issue Type",
            orientation="h",
            title="Troubleshooting coverage by issue type",
            text="Cases",
        )
        fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=55, b=10),
            showlegend=False,
            template="plotly_dark" if DARK_MODE else "plotly_white",
        )
        fig.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(fig, width="stretch")

    with c2:
        severity_counts = cases_df["severity"].value_counts().reset_index()
        severity_counts.columns = ["Severity", "Cases"]
        fig2 = px.pie(
            severity_counts,
            names="Severity",
            values="Cases",
            title="Severity mix",
            hole=.58,
        )
        fig2.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=55, b=10),
            template="plotly_dark" if DARK_MODE else "plotly_white",
            legend=dict(orientation="h", y=-.08),
        )
        st.plotly_chart(fig2, width="stretch")

    st.markdown('<div class="section-title">Diagnostic workflow</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="workflow">
          <div class="step active">01 • Select case</div><div class="step">→</div>
          <div class="step active">02 • Rule checker</div><div class="step">→</div>
          <div class="step active">03 • AI diagnosis</div><div class="step">→</div>
          <div class="step active">04 • Human review</div><div class="step">→</div>
          <div class="step">05 • Audit record</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if audit_count:
        dcounts = (
            audit["decision"]
            .value_counts()
            .reindex(["ACCEPTED", "EDITED", "REJECTED"], fill_value=0)
            .reset_index()
        )
        dcounts.columns = ["Decision", "Count"]
        fig3 = px.bar(dcounts, x="Decision", y="Count", text="Count", title="Human review outcomes")
        fig3.update_layout(
            height=300,
            template="plotly_dark" if DARK_MODE else "plotly_white",
            margin=dict(l=10, r=10, t=55, b=10),
            showlegend=False,
        )
        fig3.update_traces(textposition="outside")
        st.plotly_chart(fig3, width="stretch")
    else:
        st.info(
            "No human decisions have been logged yet. Run a diagnosis and use Approve, Edit & Accept, or Reject to populate the audit trail."
        )

# -----------------------------
# Diagnose
# -----------------------------
elif active_tab == "🧠 Diagnose":
    st.markdown(
        f"""
        <div class="case-card">
            <div class="case-id">CASE {safe_text(selected['case_id'])}</div>
            <div class="case-title">{safe_text(selected['symptom'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------
    # Case summary cards
    # -----------------------------

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Issue Type</div>
                <div class="summary-value">
                    {safe_text(selected.get("concept_tag", "Unknown"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Severity</div>
                <div class="summary-value severity-value">
                    {safe_text(selected.get("severity", "Unknown"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Expected OSI</div>
                <div class="summary-value">
                    {safe_text(selected.get("osi_layer", "Unknown"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Evidence</div>
                <div class="summary-value">
                    Show outputs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    # Keep the case evidence side-by-side, but keep the diagnosis
    # results BELOW this row at full page width.  This prevents the
    # diagnostic result from being trapped inside the right column.
    left, right = st.columns([1, 1.15])

    with left:
        st.markdown("###  Topology & symptom")

        topology = safe_text(
            selected.get(
                "topology_note",
                "No topology note provided.",
            )
        )
        symptom = safe_text(selected.get("symptom", ""))
        fault = safe_text(selected.get("expected_fault", ""))

        st.markdown(
            f"""
            <div class="evidence-card">
                <div class="evidence-text">{topology}</div>
            </div>

            <div class="subheading">Observed symptom</div>
            <div class="normal-text">{symptom}</div>

            <div class="subheading">Reference fault</div>
            <div class="normal-text">{fault}</div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("###  CLI evidence")

        cli_output = safe_text(
            selected.get(
                "show_outputs",
                "No CLI output provided.",
            )
        )

        st.markdown(
            f"""
            <div class="evidence-card cli-card">
                <pre>{cli_output}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # Diagnosis results -- FULL WIDTH
    # ---------------------------------------------------------
    result = (
        st.session_state.get("diagnosis")
        if st.session_state.get("selected_case") == selected_id
        else None
    )

    if not result:
        st.markdown(
            f"""
            <div class="ready-card">
                <div class="ready-title">Ready to diagnose</div>
                <div class="ready-text">
                    Use <strong>Run AI Diagnosis</strong> in the sidebar to start
                    the hybrid checker + AI workflow.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # This marker makes the result section visually distinct and gives
        # the browser a stable target after a diagnosis is generated.
        st.markdown(
            '<div id="diagnosis-results"></div>',
            unsafe_allow_html=True,
        )

        checker = result.get("checker", {})
        diagnosis = result.get("diagnosis", {})

        st.markdown(
            '<div class="section-title">Deterministic findings</div>',
            unsafe_allow_html=True,
        )

        if checker.get("status") == "ERRORS_DETECTED":
            st.markdown(
                f"""
                <div class="status-bad">
                    ⚠ {int(checker.get("count", 0))}
                    configuration finding(s) detected before AI reasoning
                </div>
                """,
                unsafe_allow_html=True,
            )

            for finding in checker.get("findings", []):
                rule = safe_text(finding.get("rule", "Finding"))
                sev = safe_text(finding.get("severity", ""))
                evidence = safe_text(finding.get("evidence", ""))
                recommendation = safe_text(
                    finding.get("recommendation", "")
                )

                with st.expander(
                    f"{rule} • {sev}",
                    expanded=True,
                ):
                    st.markdown(
                        f"""
                        <div class="finding-text">
                            <strong>Evidence:</strong> {evidence}
                        </div>
                        <div class="finding-text">
                            <strong>Recommendation:</strong> {recommendation}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div class="status-good">'
                '✓ No deterministic rule violation detected'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-title">AI diagnostic result</div>',
            unsafe_allow_html=True,
        )

        root_cause = str(
            diagnosis.get(
                "root_cause",
                "Unknown",
            )
        )
        osi_layer = str(
            diagnosis.get(
                "osi_layer",
                "Unknown",
            )
        )
        confidence = confidence_value(
            diagnosis.get(
                "confidence",
                0,
            )
        )

        d1, d2, d3 = st.columns([2.2, 1, 1])

        with d1:
            st.markdown(
                f"""
                <div class="diagnostic-card root-card">
                    <div class="diagnostic-label">
                         ROOT CAUSE
                    </div>
                    <div class="root-cause-text">
                        {safe_text(root_cause)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with d2:
            st.markdown(
                f"""
                <div class="diagnostic-card">
                    <div class="diagnostic-label">
                         OSI LAYER
                    </div>
                    <div class="diagnostic-value">
                        {safe_text(osi_layer)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with d3:
            st.markdown(
                f"""
                <div class="diagnostic-card confidence-card">
                    <div class="diagnostic-label">
                         CONFIDENCE
                    </div>
                    <div class="diagnostic-value">
                        {confidence:.0f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        provider = safe_text(
            diagnosis.get(
                "provider",
                "unknown",
            )
        )
        st.caption(f"Provider: **{provider}**")

        why = diagnosis.get(
            "why_this_is_happening",
            "The supplied evidence matches the diagnostic pattern for this case.",
        )
        impact = diagnosis.get(
            "impact",
            "The identified issue may affect network connectivity or service availability.",
        )
        risk = diagnosis.get(
            "risk_level",
            selected.get("severity", "Medium"),
        )

        w1, w2 = st.columns([2, 1])

        with w1:
            st.markdown(
                f"""
                <div class="result-box">
                    <div class="result-box-title">
                         Why this diagnosis?
                    </div>
                    <div class="result-box-text">
                        {safe_text(why)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with w2:
            st.markdown(
                f"""
                <div class="result-box">
                    <div class="result-box-title">
                         Risk Level
                    </div>
                    <div class="result-box-text risk-text">
                        {safe_text(risk)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="result-box">
                <div class="result-box-title">
                     Impact
                </div>
                <div class="result-box-text">
                    {safe_text(impact)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-title"> Evidence used</div>',
            unsafe_allow_html=True,
        )

        evidence = diagnosis.get("evidence", [])
        if isinstance(evidence, str):
            evidence = [evidence]

        if evidence:
            for i, ev in enumerate(evidence, 1):
                st.markdown(
                    f"""
                    <div class="result-box evidence-result">
                        <div class="result-box-title">
                            Evidence {i}
                        </div>
                        <div class="result-box-text">
                            {safe_text(ev)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No specific evidence was returned.")

        fix_steps = diagnosis.get("fix_steps", [])

        if isinstance(fix_steps, str):
            fix_steps = [fix_steps]
        elif not isinstance(fix_steps, list):
            fix_steps = [str(fix_steps)]

        fix_steps = [str(step) for step in fix_steps]

        nx, fx, vx = st.columns([1, 1.2, 1])

        with nx:
            st.markdown("###  Next command")

            next_command = str(
                diagnosis.get(
                    "next_command",
                    "",
                )
            )

            st.code(
                next_command or "No additional command provided.",
                language="text",
            )

        with fx:
            st.markdown("###  Proposed fix")

            if fix_steps:
                for i, step in enumerate(fix_steps, 1):
                    st.markdown(
                        f"""
                        <div class="fix-step">
                            <strong>{i}.</strong> {safe_text(step)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No remediation steps provided.")

        with vx:
            st.markdown("### ✅ Verification")

            verification = diagnosis.get(
                "verification",
                "Re-run the relevant show command and confirm that the reported fault is resolved.",
            )

            st.markdown(
                f"""
                <div class="verification-box">
                    {safe_text(verification)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        st.markdown(
            '<div class="section-title">Human-in-the-loop gate</div>',
            unsafe_allow_html=True,
        )

        st.warning(
            "Review the evidence and remediation before accepting. "
            "Deployment is simulated and never changes a real device."
        )

        fix_text = "\n".join(fix_steps)

        edited = st.text_area(
            "Review / edit remediation",
            value=fix_text,
            height=150,
        )

        a1, a2, a3 = st.columns(3)

        with a1:
            if st.button(
                "✅ Approve & Deploy",
                width="stretch",
            ):
                append_audit(
                    selected,
                    "ACCEPTED",
                    diagnosis,
                    edited_command=edited,
                )
                st.session_state.decision = "ACCEPTED"
                st.toast(
                    "Approval logged",
                    icon="✅",
                )
                st.rerun()

        with a2:
            if st.button(
                "✏️ Edit & Accept",
                width="stretch",
            ):
                append_audit(
                    selected,
                    "EDITED",
                    diagnosis,
                    edited_command=edited,
                    reason=(
                        "Human modified the AI recommendation "
                        "before acceptance."
                    ),
                )
                st.session_state.decision = "EDITED"
                st.toast(
                    "Edited decision logged",
                    icon="✏️",
                )
                st.rerun()

        with a3:
            if st.button(
                "❌ Reject",
                width="stretch",
            ):
                append_audit(
                    selected,
                    "REJECTED",
                    diagnosis,
                    edited_command=edited,
                    reason=(
                        "Human reviewer rejected the AI "
                        "diagnosis/fix."
                    ),
                )
                st.session_state.decision = "REJECTED"
                st.toast(
                    "Rejection logged",
                    icon="🛡️",
                )
                st.rerun()

        if st.session_state.decision:
            cls = (
                "status-good"
                if st.session_state.decision in ("ACCEPTED", "EDITED")
                else "status-bad"
            )

            st.markdown(
                f"""
                <div class="{cls}">
                    Current decision:
                    {safe_text(st.session_state.decision)}
                </div>
                """,
                unsafe_allow_html=True,
            )

# -----------------------------
# Analytics
# -----------------------------
if active_tab == "📊 Analytics":
    st.markdown('<div class="section-title">Analytics cockpit</div>', unsafe_allow_html=True)

    a1, a2 = st.columns(2)
    with a1:
        concept = cases_df.groupby(["concept_tag", "severity"]).size().reset_index(name="Cases")
        fig = px.bar(
            concept,
            x="concept_tag",
            y="Cases",
            color="severity",
            barmode="stack",
            title="Issue type × severity",
        )
        fig.update_layout(
            template="plotly_dark" if DARK_MODE else "plotly_white",
            height=380,
            margin=dict(l=10, r=10, t=55, b=10),
        )
        st.plotly_chart(fig, width="stretch")

    with a2:
        osi = cases_df["osi_layer"].value_counts().reset_index()
        osi.columns = ["OSI Layer", "Cases"]
        fig = px.bar(osi, x="OSI Layer", y="Cases", title="Case coverage by OSI layer", text="Cases")
        fig.update_layout(
            template="plotly_dark" if DARK_MODE else "plotly_white",
            height=380,
            margin=dict(l=10, r=10, t=55, b=10),
            showlegend=False,
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

    if audit_count:
        ac = audit.copy()
        ac["Confidence"] = pd.to_numeric(ac["confidence"], errors="coerce").fillna(0)
        ac["Confidence %"] = ac["Confidence"].apply(confidence_value)
        st.markdown("### Reviewed diagnosis confidence")
        fig = px.scatter(
            ac,
            x="case",
            y="Confidence %",
            color="decision",
            hover_data=["root_cause"],
            title="AI confidence at human review",
        )
        fig.update_layout(
            template="plotly_dark" if DARK_MODE else "plotly_white",
            height=360,
            margin=dict(l=10, r=10, t=55, b=10),
            yaxis_title="Confidence (%)",
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Confidence analytics will appear after the first human review decision.")

# -----------------------------
# Audit & Safety
# -----------------------------
if active_tab == "🛡️ Audit & Safety":
    st.markdown('<div class="section-title">Audit & Safety</div>', unsafe_allow_html=True)
    st.warning(
        "AI recommendations are advisory. Every remediation requires human review before simulated deployment."
    )

    if audit_count == 0:
        st.info("No audit decisions have been recorded yet.")
    else:
        accepted_count = int((audit["decision"] == "ACCEPTED").sum())
        edited_count = int((audit["decision"] == "EDITED").sum())
        rejected_count = int((audit["decision"] == "REJECTED").sum())

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Reviewed", audit_count)
        a2.metric("Accepted", accepted_count)
        a3.metric("Edited", edited_count)
        a4.metric("Rejected", rejected_count)

        st.markdown("### Decision history")
        display_audit = audit.copy()
        if "confidence" in display_audit.columns:
            display_audit["confidence"] = display_audit["confidence"].apply(
                lambda value: f"{confidence_value(value):.0f}%"
            )
        st.dataframe(display_audit, width="stretch", hide_index=True)

    st.markdown("### Safety principles")
    st.markdown(
        """
        - **Evidence first:** diagnosis is based on the supplied case evidence.
        - **Deterministic checks:** rule-based findings are evaluated before AI reasoning.
        - **Human approval:** recommendations are not automatically deployed.
        - **Simulation mode:** this application does not connect to real network devices.
        - **Audit trail:** approval, editing, and rejection decisions are recorded.
        """
    )
