from __future__ import annotations

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


def is_security_check(page_content: str, title: str = "") -> bool:
    combined = f"{title or ''} {page_content or ''}".lower()
    return any(marker in combined for marker in SECURITY_CHECK_MARKERS)


def download_career_homepage(context):
    config = context.get("config", {})
    timeout = config.get("career_timeout", config.get("timeout", 15000))
    wait_until = config.get("wait_until", "domcontentloaded")
    headless = config.get("headless", True)
    url = context.get("career_url", "")

    if not config.get("live_fetch", True):
        context.setdefault("logs", []).append("Live career-page fetch disabled; using existing HTML.")
        return context

    if not url:
        context.setdefault("errors", []).append("Missing career URL.")
        return context

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            page.goto(url, wait_until=wait_until, timeout=timeout)
            title = page.title()
            html = page.content()
            browser.close()
    except Exception as exc:
        context.setdefault("errors", []).append(f"Live career-page fetch failed for {url}: {exc}")
        context.setdefault("logs", []).append(f"Skipped {context.get('company', '')}: live fetch failed.")
        return context

    if is_security_check(html, title):
        context.setdefault("skipped", []).append(
            {
                "company": context.get("company", ""),
                "title": title,
                "url": url,
                "reason": "career homepage security verification detected",
            }
        )
        context.setdefault("logs", []).append(f"Skipped {context.get('company', '')}: security verification detected.")
        context["html"] = ""
        return context

    context["html"] = html
    context.setdefault("metadata", {})["live_career_url"] = url
    context.setdefault("logs", []).append(f"Fetched live career page: {url}")
    return context
