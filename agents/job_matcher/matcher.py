from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup


PROFILE_PATH = Path("outputs/search_profile.json")
CANDIDATE_PATH = Path("outputs/candidate_profile.json")

ROLE_TERMS = [
    "ai",
    "machine learning",
    "ml",
    "llm",
    "data scientist",
    "data engineer",
    "software engineer",
    "backend",
    "frontend",
    "full stack",
    "platform",
    "cloud",
    "devops",
    "site reliability",
    "sre",
    "quantitative",
    "research",
    "python",
    "java",
]

GENERIC_TITLES = {
    "",
    "apply",
    "apply now",
    "jobs",
    "careers",
    "open roles",
    "open opportunities",
    "students and graduates",
    "students & graduates",
    "your application",
    "training & development",
    "events",
    "search programmes",
    "research portal",
    "environmental sustainability",
    "open positions",
    "stay informed",
    "overview",
}

BAD_URL_PARTS = (
    "/solutions/",
    "/products/",
    "/data-center/",
    "/industries/",
    "/geforce/",
    "/software/",
    "/research/",
    "/blog/",
    "/news/",
    "/press",
    "/privacy",
    "/support",
    "/contact",
    "docs.",
    "developer.",
    "build.nvidia.com",
    "catalog.ngc.nvidia.com",
)

JOB_URL_PARTS = (
    "myworkdayjobs.com",
    "greenhouse.io",
    "jobs.lever.co",
    "ashbyhq.com",
    "smartrecruiters.com",
    "oraclecloud.com/hcmui/candidateexperience",
    "/job/",
    "/jobs/",
    "/careers/job",
    "/careers/jobs",
    "/jobdetails",
    "/job-detail",
    "/requisition",
    "/requisitions",
    "/open-opportunities/",
)


def _load_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def _profile_terms(context: dict | None = None) -> list[str]:
    if context and isinstance(context.get("resume_profile"), dict):
        resume_profile = context["resume_profile"]
        terms = []
        for key in ("bestTargetRoles", "searchKeywords", "skills", "specializations", "preferredLocations"):
            values = resume_profile.get(key, [])
            if isinstance(values, list):
                terms.extend(str(value).lower() for value in values)
        terms.extend(ROLE_TERMS)
        return sorted({term.strip() for term in terms if term and len(term.strip()) > 1})

    profile = _load_json(PROFILE_PATH, {})
    candidate = _load_json(CANDIDATE_PATH, {})
    terms: list[str] = []

    for key in ("bestTargetRoles", "searchKeywords", "specializations", "preferredLocations"):
        values = profile.get(key, [])
        if isinstance(values, list):
            terms.extend(str(value).lower() for value in values)

    skills = candidate.get("skills", [])
    if isinstance(skills, list):
        terms.extend(str(skill).lower() for skill in skills)

    terms.extend(ROLE_TERMS)
    return sorted({term.strip() for term in terms if term and len(term.strip()) > 1})


def _looks_like_opportunity(title: str, url: str) -> bool:
    normalized_title = title.strip().lower()
    if normalized_title in GENERIC_TITLES:
        return False

    combined = f"{title} {url}".lower()
    if any(bad in combined for bad in ("privacy", "cookie", "login", "sign-in", "support", "contact")):
        return False
    if any(bad in combined for bad in BAD_URL_PARTS):
        return False

    has_job_url = any(part in combined for part in JOB_URL_PARTS)
    has_role_term = any(term in combined for term in ROLE_TERMS)
    return has_job_url and has_role_term


def _score_link(title: str, url: str, terms: list[str]) -> int:
    combined = f"{title} {url}".lower()
    score = 0
    for term in terms:
        if term in combined:
            score += 4 if len(term.split()) > 1 else 1
    return score


def _location_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.replace("-", " ").replace("_", " ").lower()
    for location in ("bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "gurugram", "noida", "chennai", "india"):
        if location in path:
            return "Bangalore" if location == "bengaluru" else location.title()
    return "Not specified"


def _role_search_url(company: str, career_url: str, role: str) -> str:
    company_key = company.lower()
    encoded = quote_plus(role)
    if "apple" in company_key:
        return f"https://jobs.apple.com/en-us/search?search={encoded}"
    if "nvidia" in company_key:
        return f"https://jobs.nvidia.com/careers?query={encoded}"
    if "stripe" in company_key:
        return f"https://stripe.com/jobs/search?query={encoded}"
    if "google" in company_key:
        return f"https://www.google.com/about/careers/applications/jobs/results/?q={encoded}"
    if "microsoft" in company_key:
        return f"https://jobs.careers.microsoft.com/global/en/search?q={encoded}"
    separator = "&" if "?" in career_url else "?"
    return f"{career_url}{separator}q={encoded}"


def _resume_search_jobs(context, terms: list[str]) -> list[dict]:
    profile = context.get("resume_profile", {})
    roles = profile.get("bestTargetRoles") if isinstance(profile, dict) else []
    if not isinstance(roles, list) or not roles:
        roles = ["Software Engineer", "AI Engineer", "Machine Learning Engineer"]

    jobs = []
    for role in roles[:3]:
        role_text = str(role).strip()
        if not role_text:
            continue
        url = _role_search_url(context.get("company", ""), context.get("career_url", ""), role_text)
        jobs.append(
            {
                "company": context.get("company", ""),
                "role": f"{role_text} search results",
                "location": "Live company search",
                "employment_type": "Not specified",
                "experience": "Matched to uploaded resume",
                "description": (
                    "Live company career search generated from the uploaded resume. "
                    "Open the link to view current postings for this role."
                ),
                "apply_link": url,
                "match_score": _score_link(role_text, url, terms) or 1,
                "source": "live_resume_search",
            }
        )
    return jobs


def _links_from_html(html: str, base_url: str, company: str) -> list[dict]:
    links = []
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.find_all("a", href=True):
        title = anchor.get_text(" ", strip=True)
        url = urljoin(base_url, anchor["href"].strip())
        if _looks_like_opportunity(title, url):
            links.append(
                {
                    "company": company,
                    "title": title,
                    "url": url,
                }
            )
    return links


def _job_links_from_downloaded_pages(context) -> list[dict]:
    links = []
    if context.get("html"):
        links.extend(
            _links_from_html(
                context.get("html", ""),
                context.get("career_url", ""),
                context.get("company", ""),
            )
        )

    for page in context.get("job_pages", []):
        links.extend(
            _links_from_html(
                page.get("html", ""),
                page.get("url", context.get("career_url", "")),
                context.get("company", page.get("company", "")),
            )
        )
    return links


def add_resume_matched_jobs(context):
    if context.get("jobs"):
        return context

    terms = _profile_terms(context)
    fallback_jobs = []
    seen = set()

    source_links = list(context.get("job_links", [])) + _job_links_from_downloaded_pages(context)

    for link in source_links:
        title = str(link.get("title") or "").strip()
        url = str(link.get("url") or "").strip()
        if not url or url in seen:
            continue
        if not _looks_like_opportunity(title, url):
            continue

        score = _score_link(title, url, terms)
        if score < 2:
            continue

        seen.add(url)
        fallback_jobs.append(
            {
                "company": context.get("company", link.get("company", "")),
                "role": title or "Technical Opportunity",
                "location": _location_from_url(url),
                "employment_type": "Not specified",
                "experience": "Entry-Level / Early Career friendly",
                "description": (
                    "Resume-matched opportunity discovered from the company career page. "
                    "Open the apply link to verify current role details."
                ),
                "apply_link": url,
                "match_score": score,
                "source": "resume_link_fallback",
            }
        )

    fallback_jobs.sort(key=lambda job: job.get("match_score", 0), reverse=True)
    context["jobs"] = fallback_jobs[:10]
    if not context["jobs"] and context.get("config", {}).get("create_live_search_links", True):
        context["jobs"] = _resume_search_jobs(context, terms)
        if context["jobs"]:
            context.setdefault("logs", []).append(
                f"Created {len(context['jobs'])} live resume search links because exact postings were not visible."
            )
            return context

    if fallback_jobs:
        context.setdefault("logs", []).append(
            f"Resume Match fallback saved {len(context['jobs'])} relevant opportunities."
        )
    else:
        context.setdefault("logs", []).append("Resume Match fallback found no relevant opportunities.")

    return context
