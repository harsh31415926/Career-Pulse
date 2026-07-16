from agents.company_context.schema import COMPANY_CONTEXT

from agents.html_processor.loader import load_data

from agents.follow_links_extractor.extractor import extract_links

from agents.job_link_classifier.classifier import classify_links

from agents.job_page_downloader.downloader import download_pages


# ==================== Load HTML ====================

html = load_data(
    "outputs/comapnies_front_page_html/Google.html"
)

# ==================== Create Context ====================

context = COMPANY_CONTEXT.copy()

context["company"] = "Google"

context["career_url"] = "https://careers.google.com"

context["html"] = html

# ==================== Pipeline ====================

context = extract_links(context)

context = classify_links(context)

context = download_pages(context)

# ==================== Results ====================

print("=" * 80)
print(f"Downloaded {len(context['job_pages'])} pages")
print("=" * 80)

for page in context["job_pages"]:

    print(f"\nCompany : {page['company']}")
    print(f"Title   : {page['title']}")
    print(f"URL     : {page['url']}")

    print("\nHTML Preview\n")

    print(page["html"][:500])

    print("=" * 80)