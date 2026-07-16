from agents.html_processor.loader import load_data
from agents.follow_links_extractor.extractor import extract_links
from agents.company_context.schema import COMPANY_CONTEXT

html = load_data(
    "outputs/comapnies_front_page_html/Google.html"
)

context = COMPANY_CONTEXT.copy()

context["company"] = "Google"
context["career_url"] = "https://careers.google.com"
context["html"] = html

context = extract_links(context)

print(f"Found {len(context['job_links'])} links\n")

for link in context["job_links"]:
    print(link)