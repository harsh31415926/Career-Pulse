import os 

from agents.html_processor.chunker import chunk_size
from agents.html_processor.loader import load_data
from agents.html_processor.cleaner import clean_html
from agents.html_processor.extractor import extract_jobs

from .validator import validate_response
from .merger import save_jobs

HTML_FOLDER = "outputs/comapnies_front_page_html"

all_jobs = []

for filename in os.listdir(HTML_FOLDER):

    if not filename.endswith(".html"):
        continue

    print("=" * 80)
    print(f"Processing {filename}")

    path = os.path.join(
        HTML_FOLDER,
        filename
    )

    html = load_data(path)

    text = clean_html(html)

    chunks = chunk_size(text)

    for chunk in chunks:

        llm_response = extract_jobs(chunk)

        print("=" * 80)
        print(llm_response)
        print("=" * 80)

        jobs = validate_response(llm_response)

        all_jobs.extend(jobs)


save_jobs(all_jobs)