from playwright.sync_api import sync_playwright


SECURITY_CHECK_MARKERS = [
    "verify you are human",
    "performing security verification",
    "checking if the site connection is secure",
    "just a moment",
    "cf-challenge",
    "cloudflare",
    "captcha",
]


def _is_security_check(page_content, title):
    combined = f"{title or ''} {page_content or ''}".lower()
    return any(marker in combined for marker in SECURITY_CHECK_MARKERS)


def _skip_page(context, job, reason):
    message = f"Skipped {job.get('company', 'Unknown')} page: {reason} ({job.get('url', '')})"
    context.setdefault("skipped", []).append(
        {
            "company": job.get("company", ""),
            "title": job.get("title", ""),
            "url": job.get("url", ""),
            "reason": reason,
        }
    )
    context.setdefault("logs", []).append(message)
    print(message)


def download_pages(context):

    downloaded_pages = []
    config = context.get("config", {})
    headless = config.get("headless", True)
    timeout = config.get("timeout", 15000)
    wait_until = config.get("wait_until", "domcontentloaded")
    max_pages = config.get("max_pages")
    stop_on_security = config.get("stop_on_security", True)
    links = context.get("job_links", [])

    if config.get("skip_download"):
        context.setdefault("logs", []).append("Job Page Downloader skipped by configuration.")
        context["job_pages"] = []
        return context

    if max_pages:
        links = links[:max_pages]

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=headless
        )

        page = browser.new_page()

        for job in links:

            try:

                print(f"Opening {job['url']}")

                page.goto(
                    job["url"],
                    wait_until=wait_until,
                    timeout=timeout
                )

                title = page.title()
                html = page.content()

                if _is_security_check(html, title):
                    _skip_page(context, job, "security verification detected")
                    if stop_on_security:
                        context.setdefault("logs", []).append(
                            f"Stopping downloads for {context.get('company', '')} after security verification."
                        )
                        break
                    continue

                downloaded_pages.append(

                    {
                        "company": job["company"],

                        "title": job["title"],

                        "url": job["url"],

                        "html": html
                    }

                )

            except Exception as e:

                _skip_page(context, job, f"download failed: {e}")

        browser.close()

    context["job_pages"] = downloaded_pages

    return context
