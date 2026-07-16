from agents.company_context.schema import COMPANY_CONTEXT
from agents.html_processor.loader import load_data

from agents.follow_links_extractor.extractor import extract_links
from agents.job_link_classifier.classifier import classify_links


html = load_data(
    "outputs/comapnies_front_page_html/Google.html"
)

context = COMPANY_CONTEXT.copy()

context["company"] = "Google"
context["career_url"] = "https://careers.google.com"
context["html"] = html


context = extract_links(context)

print("=" * 80)
print("Before Classification")
print("=" * 80)

for link in context["job_links"]:
    print(link)


context = classify_links(context)

print("\n")
print("=" * 80)
print("After Classification")
print("=" * 80)

for link in context["job_links"]:
    print(link)