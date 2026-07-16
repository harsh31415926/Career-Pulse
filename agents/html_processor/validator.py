import json


def validate_response(response: str):
    """
    Validates and parses the JSON returned by the LLM.

    Returns:
        list: List of extracted jobs.
    """

    if not response:
        return []

    # Remove markdown code blocks
    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # Sometimes the LLM writes explanations before/after JSON
    start = response.find("[")
    end = response.rfind("]")

    if start != -1 and end != -1:
        response = response[start:end + 1]

    try:
        jobs = json.loads(response)

        if isinstance(jobs, dict):
            jobs = [jobs]

        if not isinstance(jobs, list):
            return []

        valid_jobs = []

        for job in jobs:

            if not isinstance(job, dict):
                continue

            valid_jobs.append(
                {
                    "company": job.get("company", ""),
                    "role": job.get("role", ""),
                    "location": job.get("location", ""),
                    "employment_type": job.get("employment_type", ""),
                    "experience": job.get("experience", ""),
                    "description": job.get("description", ""),
                    "apply_link": job.get("apply_link", "")
                }
            )

        return valid_jobs

    except json.JSONDecodeError:

        print("😔 Invalid JSON returned by LLM")

        return []