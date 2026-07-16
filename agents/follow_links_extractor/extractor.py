from bs4 import BeautifulSoup
from urllib.parse import urljoin


KEYWORDS = [
    "job",
    "jobs",
    "position",
    "positions",
    "opening",
    "openings",
    "vacancy",
    "vacancies",
    "career",
    "careers",
    "apply",
    "software engineer",
    "machine learning",
    "data scientist",
    "backend",
    "frontend",
    "full stack",
    "ai",
    "ml",
    "research",
    "intern",
    "graduate"
]


def extract_links(context):

    company = context["company"]
    career_url = context["career_url"]
    html = context["html"]

    soup = BeautifulSoup(html, "html.parser")

    links = []
    seen = set()

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        # Ignore invalid links
        if not href:
            continue

        if href.startswith("#"):
            continue

        if href.startswith("javascript:"):
            continue

        if href.startswith("mailto:"):
            continue

        if href.endswith(".pdf"):
            continue

        text = a.get_text(strip=True)

        combined = f"{href} {text}".lower()

        if not any(keyword in combined for keyword in KEYWORDS):
            continue

        full_url = urljoin(career_url, href)

        # Remove duplicate links
        if full_url in seen:
            continue

        seen.add(full_url)

        links.append(
            {
                "company": company,
                "title": text,
                "url": full_url
            }
        )

    context["job_links"] = links

    return context