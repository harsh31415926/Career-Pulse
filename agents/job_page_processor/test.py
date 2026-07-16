from agents.company_context.schema import COMPANY_CONTEXT

from agents.html_processor.loader import load_data

from agents.career_page_analyzer.analyzer import analyze_career_page

from agents.extraction_router.router import route

from agents.job_link_classifier.classifier import classify_links

from agents.job_page_downloader.downloader import download_pages

from agents.job_page_processor.processor import process_pages


html = load_data(
    "outputs/comapnies_front_page_html/Google.html"
)

context = COMPANY_CONTEXT.copy()

context["company"] = "Google"

context["career_url"] = "https://careers.google.com"

context["html"] = html


# ================= Pipeline =================

context = analyze_career_page(context)

print("=" * 80)
print(context)
print("=" * 80)

assert "analysis" in context
assert "strategy" in context["analysis"]    

context = route(context)

context = classify_links(context)

context = download_pages(context)

context = process_pages(context)

# ============================================

print("\n")
print("=" * 80)
print("FINAL JOBS")
print("=" * 80)

print(context["jobs"])