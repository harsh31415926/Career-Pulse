from __future__ import annotations

import re


KNOWN_SKILLS = [
    "python",
    "java",
    "sql",
    "machine learning",
    "deep learning",
    "ai",
    "artificial intelligence",
    "llm",
    "llms",
    "langchain",
    "langgraph",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "xgboost",
    "pandas",
    "numpy",
    "streamlit",
    "fastapi",
    "django",
    "flask",
    "react",
    "node",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "github",
]

ROLE_HINTS = {
    "machine learning": "Machine Learning Engineer",
    "deep learning": "Machine Learning Engineer",
    "llm": "LLM Engineer",
    "llms": "LLM Engineer",
    "langchain": "Agentic AI Engineer",
    "langgraph": "Agentic AI Engineer",
    "ai": "AI Engineer",
    "artificial intelligence": "AI Engineer",
    "python": "Software Engineer",
    "java": "Software Engineer",
    "sql": "Data Engineer",
    "pandas": "Data Scientist",
    "numpy": "Data Scientist",
    "streamlit": "Applied AI Engineer",
}


def parse_resume_profile(resume_text: str) -> dict[str, list[str] | str]:
    normalized = resume_text.lower()
    skills = [skill for skill in KNOWN_SKILLS if re.search(rf"\b{re.escape(skill)}\b", normalized)]
    roles = []
    for skill in skills:
        role = ROLE_HINTS.get(skill)
        if role and role not in roles:
            roles.append(role)

    if not roles:
        roles = ["Software Engineer", "AI Engineer", "Data Scientist"]

    keywords = sorted(set(skills + [role.lower() for role in roles]))
    return {
        "bestTargetRoles": roles[:8],
        "searchKeywords": keywords,
        "skills": skills,
        "careerSummary": "Parsed locally from the uploaded resume for live job matching.",
    }
