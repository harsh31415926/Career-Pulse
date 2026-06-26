import os
from playwright.sync_api import sync_playwright
from .load_data import load_companies

os.makedirs("outputs/comapnies_front_page_html", exist_ok=True)

companies = load_companies()

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    for company in companies:

        try:

            print("=" * 80)
            print(company["company"])

            page.goto(
                company["career_url"],
                wait_until="domcontentloaded",
                timeout=60000
            )

            html = page.content()

            filename = company["company"].replace(" ", "_") + ".html"

            with open(
                f"outputs/comapnies_front_page_html/{filename}",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(html)

            print("✓ Saved")

        except Exception as e:

            print(f"❌ Failed: {company['company']}")
            print(e)

            continue