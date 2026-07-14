from agents.html_processor.loader import load_data
from agents.html_processor.cleaner import clean_html
from agents.html_processor.chunker import chunk_size
from agents.html_processor.extractor import extract_jobs

html = load_data(
    "/Users/harshsharma/Desktop/AIProject/AgenticAI/Career_pulse/outputs/comapnies_front_page_html/Amazon.html"
)

text = clean_html(html)

chunks = chunk_size(text)

result = extract_jobs(chunks[0])

print(result)