import os
import json

from groq import Groq
from dotenv import load_dotenv

from agents.profile_builder.prompt import PROFILE_BUILDER_PROMPT
from agents.profile_builder.llm_model import GROQ_MODEL

load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


''' :============================= AGENT ==========================: '''

def build_profile(profile):

    prompt = PROFILE_BUILDER_PROMPT.format(
        profile = json.dumps(
            profile , indent= 4
        )
    )

    response = client.chat.completions.create(
        model = GROQ_MODEL,
        messages=[
            {
            'role' : 'system',  
            'content' : ''' Return only JSON file no markdown, no explaination nothing , just JSON '''

        },
        {
            'role':'user',
            'content': prompt
        }
        ],
        temperature=0
    )

    return response.choices[0].message.content

