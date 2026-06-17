RESUME_PARSER_PROMPT = """
You are an expert resume parser.

Extract the following information from the resume and return ONLY valid JSON.

{{
    "name": "",
    "email": "",
    "phone": "",
    "education": [],
    "skills": [],
    "projects": [],
    "experience": [],
    "certifications": [],
    "achievements": []
}}

Resume:

{resume}
"""





''' =============================================================================================================== '''