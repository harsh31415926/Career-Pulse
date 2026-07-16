from agents.company_context.schema import COMPANY_CONTEXT

from agents.job_saver.saver import save_jobs


context = COMPANY_CONTEXT.copy()

context["company"] = "Google"

context["jobs"] = [

    {
        "company": "Google",
        "role": "Software Engineer",
        "location": "Bangalore",
        "employment_type": "Full Time",
        "experience": "0-2 Years",
        "description": "Backend Engineer",
        "apply_link": "https://careers.google.com/jobs/123"
    },

    {
        "company": "Google",
        "role": "Machine Learning Engineer",
        "location": "Hyderabad",
        "employment_type": "Full Time",
        "experience": "1-3 Years",
        "description": "ML Team",
        "apply_link": "https://careers.google.com/jobs/456"
    }

]

save_jobs(context)