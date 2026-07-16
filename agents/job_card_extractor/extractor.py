from bs4 import BeautifulSoup
from urllib.parse import urljoin


JOB_KEYWORDS = [

    "job",
    "jobs",
    "position",
    "opening",
    "apply",
    "software",
    "engineer",
    "developer",
    "scientist",
    "research",
    "intern",
    "graduate",
    "machine learning",
    "data",
    "backend",
    "frontend",
    "full stack"

]


def extract_job_cards(context):

    pages = context["job_pages"]

    all_cards = []

    seen = set()

    for page in pages:

        soup = BeautifulSoup(
            page["html"],
            "html.parser"
        )

        for a in soup.find_all("a", href=True):

            href = a["href"].strip()

            text = a.get_text(
                strip=True
            )

            if not href:
                continue

            full_url = urljoin(
                page["url"],
                href
            )

            combined = (
                text + " " + href
            ).lower()

            if not any(
                keyword in combined
                for keyword in JOB_KEYWORDS
            ):
                continue

            if full_url in seen:
                continue

            seen.add(full_url)

            all_cards.append(

                {

                    "company": page["company"],

                    "title": text,

                    "url": full_url

                }

            )

    context["job_cards"] = all_cards

    return context