from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
except Exception:  # pragma: no cover - app still renders core tables without Plotly.
    px = None

from agents.company_discovery.load_data import load_companies
from agents.pipeline.graph import build_company_state, run_company_graph
from agents.resume_parser.profile import parse_resume_profile


ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"
JOBS_DIR = OUTPUTS / "jobs"
RUNS_DIR = OUTPUTS / "runs"
PROFILE_FILE = OUTPUTS / "search_profile.json"
CANDIDATE_FILE = OUTPUTS / "candidate_profile.json"


st.set_page_config(
    page_title="Career Pulse",
    page_icon="CP",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cp-bg: #0b0c10;
            --cp-panel: rgba(255,255,255,.055);
            --cp-panel-strong: rgba(255,255,255,.085);
            --cp-line: rgba(255,255,255,.11);
            --cp-text: #f4f5f7;
            --cp-muted: #a5adba;
            --cp-accent: #7dd3fc;
            --cp-good: #34d399;
            --cp-warn: #fbbf24;
            --cp-bad: #fb7185;
        }
        .stApp { background: var(--cp-bg); color: var(--cp-text); }
        [data-testid="stSidebar"] {
            background: #08090d;
            border-right: 1px solid var(--cp-line);
        }
        [data-testid="stSidebar"] * { color: var(--cp-text); }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1320px; }
        h1, h2, h3 { letter-spacing: 0; }
        .cp-hero {
            border: 1px solid var(--cp-line);
            border-radius: 8px;
            padding: 32px;
            background: linear-gradient(135deg, rgba(255,255,255,.08), rgba(255,255,255,.035));
            box-shadow: 0 24px 80px rgba(0,0,0,.32);
            margin-bottom: 22px;
        }
        .cp-hero h1 { font-size: 54px; line-height: 1.02; margin: 0 0 10px 0; }
        .cp-hero p { color: var(--cp-muted); font-size: 18px; max-width: 780px; margin: 0; }
        .cp-card {
            border: 1px solid var(--cp-line);
            border-radius: 8px;
            padding: 18px;
            background: var(--cp-panel);
            box-shadow: 0 16px 40px rgba(0,0,0,.22);
            height: 100%;
        }
        .cp-card-title { color: var(--cp-muted); font-size: 13px; margin-bottom: 8px; }
        .cp-card-value { font-size: 30px; font-weight: 700; }
        .cp-badge {
            display: inline-flex;
            align-items: center;
            border: 1px solid var(--cp-line);
            border-radius: 999px;
            padding: 4px 10px;
            background: var(--cp-panel-strong);
            color: var(--cp-muted);
            font-size: 12px;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .cp-pipeline {
            display: grid;
            grid-template-columns: repeat(8, minmax(96px, 1fr));
            gap: 8px;
            margin: 18px 0;
        }
        .cp-pipeline-step {
            border: 1px solid var(--cp-line);
            border-radius: 8px;
            padding: 12px;
            background: var(--cp-panel);
            min-height: 76px;
            font-size: 13px;
        }
        .cp-small { color: var(--cp-muted); font-size: 13px; }
        .stButton>button {
            border-radius: 8px;
            min-height: 44px;
            border: 1px solid rgba(125,211,252,.42);
            background: rgba(125,211,252,.12);
            color: var(--cp-text);
            font-weight: 650;
        }
        .stButton>button:hover { border-color: rgba(125,211,252,.9); color: white; }
        div[data-testid="stMetric"] {
            border: 1px solid var(--cp-line);
            border-radius: 8px;
            padding: 14px;
            background: var(--cp-panel);
        }
        @media (max-width: 900px) {
            .cp-hero h1 { font-size: 38px; }
            .cp-pipeline { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


@st.cache_data(show_spinner=False)
def get_companies() -> list[dict[str, Any]]:
    return load_companies()


def latest_run_jobs_dir() -> Path | None:
    if not RUNS_DIR.exists():
        return None
    candidates = [path / "jobs" for path in sorted(RUNS_DIR.iterdir()) if (path / "jobs").exists()]
    return candidates[-1] if candidates else None


def active_jobs_dir() -> Path | None:
    session_path = st.session_state.get("active_jobs_dir")
    if session_path:
        return Path(session_path)
    return latest_run_jobs_dir()


def jobs_csv_path(jobs_dir: Path) -> Path:
    return jobs_dir.parent / "jobs.csv"


def write_run_csv(jobs_dir: Path) -> Path | None:
    jobs = get_jobs(str(jobs_dir))
    csv_path = jobs_csv_path(jobs_dir)
    if not jobs:
        if csv_path.exists():
            csv_path.unlink()
        return None
    df = pd.DataFrame(jobs)
    columns = [
        "company",
        "role",
        "location",
        "employment_type",
        "experience",
        "apply_link",
        "match_score",
        "source",
        "description",
        "_source_file",
    ]
    ordered_columns = [column for column in columns if column in df.columns]
    df = df[ordered_columns + [column for column in df.columns if column not in ordered_columns]]
    df.to_csv(csv_path, index=False)
    return csv_path


@st.cache_data(show_spinner=False)
def get_jobs(jobs_dir: str) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    root = Path(jobs_dir)
    for path in sorted(root.glob("*.json")):
        payload = read_json(path, [])
        if isinstance(payload, list):
            for job in payload:
                if not isinstance(job, dict):
                    continue
                apply_link = str(job.get("apply_link") or "").strip()
                role = str(job.get("role") or "").strip()
                company = str(job.get("company") or "").strip()
                if not company or not role or not apply_link:
                    continue
                if apply_link.endswith("/jobs/123") or apply_link.endswith("/jobs/456"):
                    continue
                job["_source_file"] = path.name
                jobs.append(job)
    return jobs


def metric_card(label: str, value: Any, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="cp-card">
            <div class="cp-card-title">{label}</div>
            <div class="cp-card-value">{value}</div>
            <div class="cp-small">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, caption: str = "") -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)


def badges(items: list[str], limit: int = 18) -> None:
    html = "".join(f'<span class="cp-badge">{item}</span>' for item in items[:limit])
    st.markdown(html or '<span class="cp-small">No data yet</span>', unsafe_allow_html=True)


def landing_page() -> None:
    st.markdown(
        """
        <div class="cp-hero">
            <h1>Career Pulse</h1>
            <p>AI Powered Career Intelligence Platform for discovering technical roles directly from company career pages.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    steps = ["Resume", "Profile", "Companies", "Career Pages", "AI Extraction", "Structured Jobs", "Matching", "Dashboard"]
    st.markdown(
        '<div class="cp-pipeline">'
        + "".join(f'<div class="cp-pipeline-step"><b>{i + 1}</b><br>{step}</div>' for i, step in enumerate(steps))
        + "</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    features = [
        ("Agentic Workflow", "LangGraph nodes wrap the existing backend modules."),
        ("Direct Discovery", "Targets company career pages instead of job boards."),
        ("LLM Extraction", "Converts messy HTML into structured job records."),
        ("Premium Dashboard", "Tracks companies, jobs, logs, and pipeline health."),
    ]
    for col, (title, text) in zip(cols, features):
        with col:
            metric_card(title, "Ready", text)


def dashboard_page() -> None:
    companies = get_companies()
    current_jobs_dir = active_jobs_dir()
    jobs = get_jobs(str(current_jobs_dir)) if current_jobs_dir else []
    job_df = pd.DataFrame(jobs)
    html_count = len(list((OUTPUTS / "comapnies_front_page_html").glob("*.html")))
    errors = sum(len(result.get("errors", [])) for result in st.session_state.get("last_run", []))

    cols = st.columns(6)
    values = [
        ("Companies", len(companies), "Loaded targets"),
        ("Legacy Snapshots", html_count, "Not used for live runs"),
        ("Pages Crawled", sum(len(r.get("job_pages", [])) for r in st.session_state.get("last_run", [])), "Latest run"),
        ("Jobs", len(jobs), "Saved records"),
        ("Today's Jobs", len(jobs), "Current dataset"),
        ("Errors", errors, "Latest run"),
    ]
    for col, (label, value, caption) in zip(cols, values):
        with col:
            metric_card(label, value, caption)

    section_header("Recent Activity", "Latest graph execution logs.")
    logs = [line for result in st.session_state.get("last_run", []) for line in result.get("logs", [])]
    st.code("\n".join(logs[-30:]) or "No pipeline run in this session yet.", language="text")

    section_header("Job Mix", "Saved extraction output.")
    st.caption(f"Showing latest run from `{current_jobs_dir}`" if current_jobs_dir else "No live run yet.")
    if not job_df.empty and "company" in job_df:
        st.dataframe(job_df, use_container_width=True, hide_index=True)
    else:
        st.info("No extracted job records are available yet.")


def resume_page() -> None:
    section_header("Resume", "Upload a PDF and inspect the parsed text before building a profile.")
    uploaded = st.file_uploader("Resume PDF", type=["pdf"])
    if uploaded:
        from agents.resume_parser.resume_parser import resume_parser

        tmp_path = ROOT / "outputs" / "uploaded_resume.pdf"
        tmp_path.write_bytes(uploaded.getbuffer())
        text = resume_parser(str(tmp_path))
        st.session_state["resume_text"] = text
        st.session_state["resume_profile"] = parse_resume_profile(text)
        st.text_area("Parsed Resume", text, height=360)
        st.markdown("**Parsed Match Profile**")
        st.json(st.session_state["resume_profile"])
    elif "resume_text" in st.session_state:
        st.text_area("Parsed Resume", st.session_state["resume_text"], height=360)
    else:
        candidate = read_json(CANDIDATE_FILE, {})
        if candidate:
            st.json(candidate)
        else:
            st.info("Upload a resume PDF to parse it.")


def profile_page() -> None:
    profile = st.session_state.get("resume_profile") or read_json(PROFILE_FILE, {})
    candidate = read_json(CANDIDATE_FILE, {})
    section_header("AI Search Profile", "Target roles, skills, seniority, and locations.")
    cols = st.columns([1, 1])
    with cols[0]:
        st.markdown("**Target Roles**")
        badges(profile.get("bestTargetRoles", []))
        st.markdown("**Preferred Locations**")
        badges(profile.get("preferredLocations", []))
    with cols[1]:
        st.markdown("**Search Keywords**")
        badges(profile.get("searchKeywords", []))
        st.markdown("**Candidate Skills**")
        badges(candidate.get("skills", []))
    st.text_area("Career Summary", profile.get("careerSummary", ""), height=130)


def companies_page() -> None:
    section_header("Companies", "Search, filter, and inspect live career-page targets.")
    df = pd.DataFrame(get_companies())
    query = st.text_input("Search companies", placeholder="Search by name or URL")
    if query and not df.empty:
        mask = df.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        df = df[mask]
    if not df.empty:
        df["html_snapshot"] = df["company"].apply(
            lambda name: (OUTPUTS / "comapnies_front_page_html" / f"{name.replace(' ', '_')}.html").exists()
        )
    st.dataframe(df, use_container_width=True, hide_index=True)


def discover_jobs_page() -> None:
    section_header("Discover Jobs", "Upload a resume, fetch live career pages, and save this run's matching jobs.")
    uploaded = st.file_uploader("Upload resume for this search", type=["pdf"], key="discover_resume_upload")
    if uploaded:
        from agents.resume_parser.resume_parser import resume_parser

        tmp_path = OUTPUTS / "uploaded_resume.pdf"
        tmp_path.write_bytes(uploaded.getbuffer())
        resume_text = resume_parser(str(tmp_path))
        st.session_state["resume_text"] = resume_text
        st.session_state["resume_profile"] = parse_resume_profile(resume_text)

    resume_profile = st.session_state.get("resume_profile")
    if resume_profile:
        st.success("Resume parsed. This run will match jobs against the uploaded resume.")
        with st.expander("Parsed resume matching profile"):
            st.json(resume_profile)
    else:
        st.warning("Upload a resume first. If you run without uploading, Career Pulse will use the old default profile.")
        resume_profile = read_json(PROFILE_FILE, {})

    companies = get_companies()
    max_companies = st.slider("Maximum companies", 1, max(len(companies), 1), min(3, max(len(companies), 1)))
    max_pages = st.slider("Maximum pages per company", 1, 50, 8)
    headless = st.toggle("Run browser in background", value=True)
    skip_download = st.toggle("Fast mode: match live career links only", value=False)
    use_llm = st.toggle("Use Groq LLM extraction", value=False)
    timeout = st.number_input("Page timeout (ms)", min_value=5000, max_value=120000, value=15000, step=5000)

    if st.button("Start Career Pulse", use_container_width=True):
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_jobs_dir = RUNS_DIR / run_id / "jobs"
        run_jobs_dir.mkdir(parents=True, exist_ok=True)
        st.session_state["active_jobs_dir"] = str(run_jobs_dir)
        progress = st.progress(0)
        log_box = st.empty()
        results = []
        start = time.perf_counter()
        selected = companies[:max_companies]

        for index, company in enumerate(selected, start=1):
            state = build_company_state(
                company,
                config={
                    "headless": headless,
                    "timeout": timeout,
                    "wait_until": "domcontentloaded",
                    "max_pages": max_pages,
                    "skip_download": skip_download,
                    "stop_on_security": True,
                    "use_llm_extraction": use_llm,
                    "create_live_search_links": True,
                    "live_fetch": True,
                    "jobs_output_dir": str(run_jobs_dir),
                    "resume_profile": resume_profile,
                },
            )
            state = run_company_graph(state)
            results.append(state)
            progress.progress(index / len(selected), text=f"Processed {company['company']}")
            logs = [line for result in results for line in result.get("logs", [])]
            log_box.code("\n".join(logs[-40:]) or "Preparing graph...", language="text")

        st.session_state["last_run"] = results
        st.session_state["last_run_seconds"] = round(time.perf_counter() - start, 2)
        get_jobs.clear()
        csv_path = write_run_csv(run_jobs_dir)
        st.session_state["active_jobs_csv"] = str(csv_path) if csv_path else ""
        st.success(f"Pipeline finished in {st.session_state['last_run_seconds']}s")
        st.info(f"This run saved jobs to `{run_jobs_dir}`")
        if csv_path:
            st.info(f"Download CSV saved at `{csv_path}`")

    results = st.session_state.get("last_run", [])
    if results:
        cols = st.columns(4)
        with cols[0]:
            metric_card("Companies", len(results), "Latest run")
        with cols[1]:
            metric_card("Links", sum(len(r.get("job_links", [])) for r in results), "Classified")
        with cols[2]:
            metric_card("Pages", sum(len(r.get("job_pages", [])) for r in results), "Downloaded")
        with cols[3]:
            metric_card("Jobs", sum(len(r.get("jobs", [])) for r in results), "Extracted")
        saved_paths = [
            r.get("metadata", {}).get("jobs_output_path")
            for r in results
            if r.get("metadata", {}).get("jobs_output_path")
        ]
        if saved_paths:
            st.markdown("**Saved Files**")
            st.code("\n".join(saved_paths), language="text")
        csv_path = st.session_state.get("active_jobs_csv")
        if csv_path:
            st.markdown("**Run CSV**")
            st.code(csv_path, language="text")
        skipped = sum(len(r.get("skipped", [])) for r in results)
        if skipped:
            st.warning(f"Skipped {skipped} blocked or failed pages. See Logs for details.")


def extracted_jobs_page() -> None:
    section_header("Extracted Jobs", "Search, filter, export, and inspect structured job records.")
    current_jobs_dir = active_jobs_dir()
    st.caption(f"Reading from `{current_jobs_dir}`" if current_jobs_dir else "No live run selected yet.")
    if st.button("Refresh saved jobs"):
        get_jobs.clear()
        st.rerun()
    jobs = get_jobs(str(current_jobs_dir)) if current_jobs_dir else []
    df = pd.DataFrame(jobs)
    if df.empty:
        st.info("No valid jobs from a live run yet. Upload a resume on Discover Jobs, click Start Career Pulse, then come back here.")
        return

    query = st.text_input("Search jobs", placeholder="Role, company, skill, location")
    if query:
        mask = df.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        df = df[mask]

    companies = sorted(df.get("company", pd.Series(dtype=str)).dropna().unique())
    selected = st.multiselect("Company filter", companies)
    if selected and "company" in df:
        df = df[df["company"].isin(selected)]

    csv_path = jobs_csv_path(current_jobs_dir)
    if csv_path.exists():
        st.download_button(
            "Download Saved Run CSV",
            csv_path.read_bytes(),
            "career_pulse_jobs.csv",
            "text/csv",
        )
    st.download_button("Export Current View CSV", df.to_csv(index=False), "career_pulse_filtered_jobs.csv", "text/csv")
    st.download_button("Export JSON", df.to_json(orient="records", indent=2), "career_pulse_jobs.json", "application/json")
    st.dataframe(df, use_container_width=True, hide_index=True)

    for job in df.to_dict("records")[:20]:
        with st.expander(f"{job.get('role', 'Unknown role')} at {job.get('company', 'Unknown company')}"):
            st.write(job.get("description", "No description available."))
            if job.get("apply_link"):
                st.link_button("Apply", job["apply_link"])


def analytics_page() -> None:
    section_header("Analytics", "Distribution and extraction performance from saved jobs.")
    current_jobs_dir = active_jobs_dir()
    jobs = get_jobs(str(current_jobs_dir)) if current_jobs_dir else []
    df = pd.DataFrame(jobs)
    if df.empty:
        st.info("Analytics will appear after jobs are extracted.")
        return
    if px is None:
        st.dataframe(df.describe(include="all"), use_container_width=True)
        return

    cols = st.columns(2)
    for col, field, title in [
        (cols[0], "company", "Jobs per Company"),
        (cols[1], "location", "Jobs per Location"),
    ]:
        with col:
            if field in df:
                chart_df = df[field].fillna("Unknown").value_counts().reset_index()
                chart_df.columns = [field, "jobs"]
                st.plotly_chart(px.bar(chart_df, x=field, y="jobs", title=title), use_container_width=True)

    if "role" in df:
        chart_df = df["role"].fillna("Unknown").value_counts().head(12).reset_index()
        chart_df.columns = ["role", "jobs"]
        st.plotly_chart(px.bar(chart_df, x="jobs", y="role", orientation="h", title="Top Roles"), use_container_width=True)


def settings_page() -> None:
    section_header("Settings", "Runtime defaults for local discovery sessions.")
    st.text_input("Groq API Key", type="password", placeholder="Set GROQ_API_KEY in your environment for backend calls")
    st.number_input("Chunk Size", min_value=1000, max_value=20000, value=6000, step=500)
    st.number_input("Maximum Pages", min_value=1, max_value=200, value=25)
    st.text_input("Output Folder", value=str(OUTPUTS))
    st.toggle("Debug Mode", value=False)


def logs_page() -> None:
    section_header("Logs", "Graph node logs, warnings, and errors from the current session.")
    results = st.session_state.get("last_run", [])
    logs = [line for result in results for line in result.get("logs", [])]
    errors = [line for result in results for line in result.get("errors", [])]
    skipped = [item for result in results for item in result.get("skipped", [])]
    st.code("\n".join(logs) or "No logs yet.", language="text")
    if skipped:
        st.markdown("**Skipped Pages**")
        st.dataframe(pd.DataFrame(skipped), use_container_width=True, hide_index=True)
    if errors:
        st.error("\n".join(errors))


def about_page() -> None:
    section_header("About", "Career Pulse architecture and roadmap.")
    st.markdown(
        """
        Career Pulse is an AI-powered career intelligence platform that discovers jobs directly from company career pages.

        **Architecture:** Streamlit UI, modular Python agents, LangGraph orchestration, Playwright crawling, BeautifulSoup parsing, Groq-backed extraction, and JSON storage.

        **Roadmap:** ATS-specific extractors, resume matching, ranking, application tracking, PostgreSQL, FastAPI, vector search, LangSmith observability, and scheduled discovery.
        """
    )


def main() -> None:
    inject_theme()
    pages = {
        "Dashboard": dashboard_page,
        "Resume": resume_page,
        "Profile": profile_page,
        "Companies": companies_page,
        "Discover Jobs": discover_jobs_page,
        "Extracted Jobs": extracted_jobs_page,
        "Analytics": analytics_page,
        "Settings": settings_page,
        "Logs": logs_page,
        "About": about_page,
    }

    st.sidebar.markdown("## Career Pulse")
    st.sidebar.caption("Agentic career intelligence")
    choice = st.sidebar.radio("Navigation", list(pages), label_visibility="collapsed")
    if choice == "Dashboard":
        landing_page()
    pages[choice]()


if __name__ == "__main__":
    main()
