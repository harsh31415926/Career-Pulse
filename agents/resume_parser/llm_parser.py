import json
import os 

from groq import Groq
from dotenv import load_dotenv

from agents.resume_parser.agents_prompts import RESUME_PARSER_PROMPT
from agents.resume_parser.file_paths import RESUME_PATH
from agents.resume_parser.model import LLM_MODEL
from agents.resume_parser.resume_parser import resume_parser

load_dotenv()


client = Groq(
    api_key = os.getenv('GROQ_API_KEY')
)


''' : ================== resume parser LLM ======================== :'''


def parse_resume_with_llm(resume_text):
    
    prompt = RESUME_PARSER_PROMPT.format(
        resume = resume_text
    )
    
    response = client.chat.completions.create(
        model = LLM_MODEL,
        messages = [
            {
                'role' : 'system',
                'content' : 'return a valid JSON '
            },
            {
                'role' : 'user',
                'content' : prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


resume_text = resume_parser(RESUME_PATH)
# print(resume_text)

llm_parced_resume_text_json = parse_resume_with_llm(resume_text)
# print(llm_parced_resume_text_json)
