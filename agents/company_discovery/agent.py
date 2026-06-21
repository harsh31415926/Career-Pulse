import json
import os

from groq import Groq
from dotenv import load_dotenv

from .prompt import COMPANY_DISCOVERY_PROMPT
from .llm_model import GROQ_MODEL

load_dotenv()

client = Groq(
    api_key= os.getenv("GROQ_API_KEY")
)



def discover_companies(search_profile):

    prompt = COMPANY_DISCOVERY_PROMPT.format(
        profile = json.dumps(search_profile, indent = 4)
    )

    response = client.chat.completions.create(
        model = GROQ_MODEL,
        messages=[
            {
                'role': 'system',
                'content': 'Return only valid JSON, no extra and nothing just JSON'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content

