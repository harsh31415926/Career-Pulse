from __future__ import annotations

from typing import TypedDict


JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonDict = dict[str, JsonValue]


class CareerPulseState(TypedDict, total=False):
    company: str
    career_url: str
    html: str
    analysis: JsonDict
    job_links: list[JsonDict]
    job_pages: list[JsonDict]
    job_cards: list[JsonDict]
    jobs: list[JsonDict]
    logs: list[str]
    statistics: JsonDict
    errors: list[str]
    skipped: list[JsonDict]
    metadata: JsonDict
    config: JsonDict
    resume_profile: JsonDict


def create_initial_state(
    *,
    company: str = "",
    career_url: str = "",
    html: str = "",
    config: JsonDict | None = None,
) -> CareerPulseState:
    return {
        "company": company,
        "career_url": career_url,
        "html": html,
        "analysis": {},
        "job_links": [],
        "job_pages": [],
        "job_cards": [],
        "jobs": [],
        "logs": [],
        "statistics": {},
        "errors": [],
        "skipped": [],
        "metadata": {},
        "config": config or {},
        "resume_profile": {},
    }
