JOB_EXTRACTION_PROMPT = """
You are an expert AI Recruitment Parser.

You are given the visible text extracted from a company's career page.

Extract ONLY active technical job openings.

Include only these roles:

- Machine Learning
- AI Engineer
- Data Scientist
- Software Engineer
- Backend Engineer
- Frontend Engineer
- Full Stack Engineer
- Platform Engineer
- Cloud Engineer
- DevOps Engineer
- Site Reliability Engineer
- Quantitative Developer
- Quantitative Researcher
- Data Engineer
- NLP Engineer
- Computer Vision Engineer

Ignore:

- Navigation menus
- Footer
- Cookie banners
- Company information
- Blog posts
- Press releases
- Legal text
- Internships (unless explicitly requested)
- HR jobs
- Sales jobs
- Marketing jobs

Return ONLY valid JSON.

Schema:

[
    {
        "company": "",
        "role": "",
        "location": "",
        "employment_type": "",
        "experience": "",
        "description": "",
        "apply_link": ""
    }
]

Career Page Text:

{text}
"""