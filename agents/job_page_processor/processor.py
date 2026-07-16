from agents.html_processor.cleaner import clean_html
from agents.html_processor.chunker import chunk_size
from agents.html_processor.extractor import extract_jobs

from agents.html_processor.validator import validate_response


def process_pages(context):

    all_jobs = []
    use_llm = context.get("config", {}).get("use_llm_extraction", False)

    if not use_llm:
        context.setdefault("logs", []).append("LLM extraction disabled; deterministic link matcher will inspect downloaded pages.")
        context["jobs"] = []
        return context

    for page in context["job_pages"]:

        print("=" * 80)
        print(f"Processing : {page['title']}")
        print("=" * 80)

        html = page["html"]

        text = clean_html(html)

        chunks = chunk_size(text)

        for chunk in chunks:

            try:
                llm_response = extract_jobs(chunk)
            except Exception as exc:
                context.setdefault("logs", []).append(f"LLM extraction failed: {exc}")
                continue

            jobs = validate_response(llm_response)

            if jobs:

                all_jobs.extend(jobs)

    context["jobs"] = all_jobs

    return context
