from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Callable

from agents.career_page_analyzer.analyzer import analyze_career_page
from agents.career_page_downloader.downloader import download_career_homepage
from agents.company_discovery.load_data import load_companies
from agents.extraction_router.router import route
from agents.html_processor.loader import load_data
from agents.job_link_classifier.classifier import classify_links
from agents.job_matcher.matcher import add_resume_matched_jobs
from agents.job_page_downloader.downloader import download_pages
from agents.job_page_processor.processor import process_pages
from agents.job_saver.saver import save_jobs
from agents.pipeline.state import CareerPulseState, create_initial_state

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover - keeps the existing pipeline usable without LangGraph.
    END = START = None
    StateGraph = None


HTML_FOLDER = Path("outputs/comapnies_front_page_html")


def _append_log(state: CareerPulseState, message: str) -> None:
    state.setdefault("logs", []).append(message)


def _run_node(
    state: CareerPulseState,
    name: str,
    fn: Callable[[CareerPulseState], CareerPulseState],
) -> CareerPulseState:
    started = time.perf_counter()
    try:
        _append_log(state, f"{name} started")
        state = fn(state)
        duration = round(time.perf_counter() - started, 2)
        _append_log(state, f"{name} completed in {duration}s")
    except Exception as exc:
        message = f"{name} failed: {exc}"
        state.setdefault("errors", []).append(message)
        _append_log(state, message)
    return state


def analyzer_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "Career Page Analyzer", analyze_career_page)


def career_downloader_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "Live Career Page Downloader", download_career_homepage)


def router_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "Extraction Router", route)


def classifier_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "Job Link Classifier", classify_links)


def downloader_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "Job Page Downloader", download_pages)


def processor_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "HTML Processor", process_pages)


def matcher_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "Resume Match Fallback", add_resume_matched_jobs)


def saver_node(state: CareerPulseState) -> CareerPulseState:
    return _run_node(state, "Job Saver", save_jobs)


def stats_node(state: CareerPulseState) -> CareerPulseState:
    state["statistics"] = {
        "links_found": len(state.get("job_links", [])),
        "pages_downloaded": len(state.get("job_pages", [])),
        "jobs_extracted": len(state.get("jobs", [])),
        "skipped": len(state.get("skipped", [])),
        "errors": len(state.get("errors", [])),
    }
    return state


def build_company_graph() -> Any:
    if StateGraph is None:
        return None

    graph = StateGraph(CareerPulseState)
    graph.add_node("career_downloader", career_downloader_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("router", router_node)
    graph.add_node("classifier", classifier_node)
    graph.add_node("downloader", downloader_node)
    graph.add_node("processor", processor_node)
    graph.add_node("matcher", matcher_node)
    graph.add_node("saver", saver_node)
    graph.add_node("stats", stats_node)

    graph.add_edge(START, "career_downloader")
    graph.add_edge("career_downloader", "analyzer")
    graph.add_edge("analyzer", "router")
    graph.add_edge("router", "classifier")
    graph.add_edge("classifier", "downloader")
    graph.add_edge("downloader", "processor")
    graph.add_edge("processor", "matcher")
    graph.add_edge("matcher", "saver")
    graph.add_edge("saver", "stats")
    graph.add_edge("stats", END)
    return graph.compile()


def _run_sequential_fallback(state: CareerPulseState) -> CareerPulseState:
    for node in (
        career_downloader_node,
        analyzer_node,
        router_node,
        classifier_node,
        downloader_node,
        processor_node,
        matcher_node,
        saver_node,
        stats_node,
    ):
        state = node(state)
    return state


def run_company_graph(state: CareerPulseState) -> CareerPulseState:
    graph = build_company_graph()
    if graph is None:
        return _run_sequential_fallback(state)
    return graph.invoke(state)


def build_company_state(
    company: dict[str, Any],
    *,
    html_folder: str | os.PathLike[str] = HTML_FOLDER,
    config: dict[str, Any] | None = None,
) -> CareerPulseState:
    name = company.get("company", "")
    html_path = Path(html_folder) / f"{name.replace(' ', '_')}.html"
    state = create_initial_state(
        company=name,
        career_url=company.get("career_url", ""),
        config=config,
    )
    if config and isinstance(config.get("resume_profile"), dict):
        state["resume_profile"] = config["resume_profile"]

    if config and config.get("live_fetch", True):
        state["metadata"] = {"html_path": str(html_path), "live_fetch": True}
        return state

    if not html_path.exists():
        state["errors"].append(f"HTML file not found: {html_path}")
        state["statistics"] = {"links_found": 0, "pages_downloaded": 0, "jobs_extracted": 0, "errors": 1}
        return state

    state["html"] = load_data(str(html_path))
    state["metadata"] = {"html_path": str(html_path)}
    return state


def run_pipeline_graph(
    *,
    max_companies: int | None = None,
    config: dict[str, Any] | None = None,
) -> list[CareerPulseState]:
    companies = load_companies()
    if max_companies:
        companies = companies[:max_companies]

    results: list[CareerPulseState] = []
    for company in companies:
        state = build_company_state(company, config=config)
        if state.get("html") or state.get("config", {}).get("live_fetch", True):
            state = run_company_graph(state)
        results.append(state)
    return results
