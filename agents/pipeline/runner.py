from agents.company_discovery.load_data import load_companies
from agents.pipeline.graph import build_company_state, run_company_graph


def run_pipeline():

    companies = load_companies()

    for company in companies:

        print("\n" + "=" * 80)
        print(f"Processing : {company['company']}")
        print("=" * 80)

        context = build_company_state(company)
        if context.get("html"):
            context = run_company_graph(context)

        print()

        print(f"Company       : {context['company']}")
        print(f"Links Found   : {len(context['job_links'])}")
        print(f"Pages Downloaded : {len(context['job_pages'])}")
        print(f"Jobs Extracted: {len(context['jobs'])}")

        print("=" * 80)


if __name__ == "__main__":

    run_pipeline()
