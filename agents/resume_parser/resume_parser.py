import fitz

''' ============: LOCAL IMPORTS :==============='''

from agents.resume_parser.file_paths import RESUME_PATH
from agents.resume_parser.agents_prompts import RESUME_PARSER_PROMPT


''' ====================: Extract Text from Resume :=================== '''

def resume_parser(pdf_path):
    doc = fitz.open(pdf_path)

    text = ''

    for page in doc :
        text+=page.get_text()

    return text

# s = resume_parser(RESUME_PATH)
# print(s)