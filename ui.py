import json
import os

import requests
import streamlit as st

st.set_page_config(page_title="Agentic PR Pipeline", page_icon="🔍", layout="wide")

st.title("🤖 Agentic PR Pipeline")
st.caption("Paste your code and get an AI-powered multi-agent review — security, performance, tests, and docs.")

with st.sidebar:
    st.header("⚙️ Settings")
    api_base = st.text_input("API Base URL", value=os.getenv("API_BASE_URL", "http://127.0.0.1:8000"))
    language = st.selectbox("Language", ["python", "javascript", "typescript"])
    approval_status = st.selectbox(
        "Approval Status",
        ["not_required", "pending", "approved", "rejected"],
    )
    st.divider()
    st.info("Start the backend first:\n```\nuvicorn src.api.app:app --reload\n```")

code = st.text_area("📋 Paste your code here", height=280, value="def add(a, b):\n    return a + b\n")

run = st.button("▶ Run Review", type="primary", use_container_width=True)

if run:
    if not code.strip():
        st.error("Code input is empty.")
        st.stop()

    try:
        with st.spinner("🔄 Running multi-agent review..."):
            resp = requests.post(
                f"{api_base}/review",
                json={"code": code, "language": language, "approval_status": approval_status},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        st.error(f"❌ Request failed: {exc}")
        st.stop()

    # ── Top-level status bar ──────────────────────────────────────────────
    risk = float(data.get("risk_score") or 0)
    approval_required = data.get("approval_required", False)
    validation_status = (data.get("validation") or {}).get("status", "unknown")

    if risk >= 0.7:
        st.error(f"🚨 High Risk — score {risk:.1f}. Human approval required.")
    elif risk >= 0.4:
        st.warning(f"⚠️ Medium Risk — score {risk:.1f}.")
    else:
        st.success(f"✅ Low Risk — score {risk:.1f}. Looks good!")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Last Agent", data.get("last_completed_agent", "—"))
    c2.metric("Risk Score", f"{risk:.2f}")
    c3.metric("Approval", "Required 🔴" if approval_required else "Not needed ✅")
    c4.metric("Validation", validation_status.upper())

    st.divider()

    # ── Pipeline flow ─────────────────────────────────────────────────────
    st.subheader("🔁 Pipeline Flow")
    execution_log = data.get("execution_log", [])
    diagnostics = data.get("llm_diagnostics", {})

    if execution_log:
        cols = st.columns(len(execution_log))
        for i, entry in enumerate(execution_log):
            agent = entry.get("agent", "?")
            source = entry.get("source", "?")
            summary = entry.get("summary", "")
            badge = "🟢 chatgroq" if source == "chatgroq" else "🟡 fallback"
            with cols[i]:
                st.markdown(f"**{agent.upper()}**")
                st.caption(badge)
                if "risk_score" in entry:
                    st.caption(f"Risk: {entry['risk_score']:.1f}")
                with st.expander("Details"):
                    st.write(summary)
    else:
        st.info("No execution log available.")

    st.divider()

    # ── Content tabs ──────────────────────────────────────────────────────
    tabs = st.tabs(["📄 PR Report", "🧪 Tests", "📚 Docs", "🔒 Security", "⚡ Performance", "🔧 Raw"])

    with tabs[0]:  # PR Report
        pr_md = data.get("pr_report_markdown", "")
        if pr_md:
            st.markdown(pr_md)
        else:
            st.info("No PR report generated.")

    with tabs[1]:  # Tests
        test_suite = data.get("test_suite", "")
        if test_suite:
            st.code(test_suite, language=language)
        else:
            st.info("No tests generated.")

    with tabs[2]:  # Docs
        docs = data.get("docs", "")
        if docs:
            st.markdown(docs)
        else:
            st.info("No documentation generated.")

    with tabs[3]:  # Security
        sec = data.get("security_notes", "")
        if sec:
            st.warning(sec)
        else:
            st.success("✅ No security issues found.")

    with tabs[4]:  # Performance
        perf = data.get("performance_notes", "")
        if perf:
            st.info(perf)
        else:
            st.success("✅ No performance issues found.")

    with tabs[5]:  # Raw
        with st.expander("Full JSON Response", expanded=False):
            st.json(data)