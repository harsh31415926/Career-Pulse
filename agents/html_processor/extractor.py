import os 

from groq import Groq
from dotenv import load_dotenv

from .prompt import JOB_EXTRACTION_PROMPT

load_dotenv()

client = Groq(api_key= os.getenv("GROQ_API_KEY"))



''' ================== Extract Jobs man ========================== '''

def extract_jobs(text):
    pass