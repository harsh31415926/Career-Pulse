from .words import GOOD_WORDS, BAD_WORDS


JOB_URL_PARTS = (
    "jobs.",
    "careers.",
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
    "/open-opportunities",
)

LISTING_WORDS = (
    "open positions",
    "open roles",
    "job search",
    "search jobs",
    "view jobs",
    "apply now",
    "opportunities",
)

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


def _score_link(title, url):
    combined = f"{title} {url}".lower()
    if any(word in combined for word in BAD_WORDS):
        return -1
    if any(part in combined for part in BAD_URL_PARTS):
        return -1

    score = 0
    if any(part in combined for part in JOB_URL_PARTS):
        score += 10
    if any(word in combined for word in LISTING_WORDS):
        score += 8
    if any(word in combined for word in GOOD_WORDS):
        score += 2
    return score

def classify_links(context):

    scored_links = []
    seen = set()

    for link in context["job_links"]:

        title = link.get("title", "").lower()

        url = link.get("url", "").lower()

        if url in seen:
            continue

        score = _score_link(title, url)
        if score <= 0:
            continue

        seen.add(url)
        scored_links.append((score, link))

    scored_links.sort(key=lambda item: item[0], reverse=True)
    context["job_links"] = [link for _, link in scored_links]

    return context
