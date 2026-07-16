from agents.company_context.schema import COMPANY_CONTEXT

from agents.html_processor.loader import load_data

from agents.job_card_extractor.extractor import extract_job_cards


context = COMPANY_CONTEXT.copy()

context["company"] = "Google"

context["job_pages"] = [

    {

        "company": "Google",

        "title": "Jobs",

        "url": "https://careers.google.com/jobs/results",

        "html": load_data(
            "outputs/comapnies_front_page_html/Google.html"
        )

    }

]

context = extract_job_cards(context)

print()

print("=" * 80)

print(f"Found {len(context['job_cards'])} job cards.")

print("=" * 80)

for card in context["job_cards"][:20]:

    print(card)