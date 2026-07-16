from agents.html_processor.loader import load_data
from agents.career_page_analyzer.analyzer import analyze_career_page

html = load_data(
    "outputs/comapnies_front_page_html/Google.html"
)

analysis = analyze_career_page(
    "Google",
    html
)

print(analysis)