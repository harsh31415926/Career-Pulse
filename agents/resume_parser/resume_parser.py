try:
    import pymupdf
except ImportError:  # PyMuPDF historically exposed this module name.
    import fitz as pymupdf

''' ============: LOCAL IMPORTS :==============='''

from agents.resume_parser.file_paths import RESUME_PATH
from agents.resume_parser.agents_prompts import RESUME_PARSER_PROMPT


''' ====================: Extract Text from Resume :=================== '''

def resume_parser(pdf_path):
    doc = pymupdf.open(pdf_path)

    text = ''

    for page in doc :
        text+=page.get_text()

    return text

# s = resume_parser(RESUME_PATH)
# print(s)
