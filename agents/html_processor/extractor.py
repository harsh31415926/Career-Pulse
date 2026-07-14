import os 

from groq import Groq
from dotenv import load_dotenv

from .prompt import JOB_EXTRACTION_PROMPT

load_dotenv()

client = Groq(api_key= os.getenv("GROQ_API_KEY"))



''' ================== Extract Jobs man ========================== '''

def extract_jobs(text):
    prompt = JOB_EXTRACTION_PROMPT.format(text= text)

    response = client.chat.completions.create(

        model = "llama-3.3-70b-versatile",

        messages=[
            {
            'role' : 'user' , 
            'content': prompt
        }
        ],
        temperature=0
    )

    return (response.choices[0].message.content)