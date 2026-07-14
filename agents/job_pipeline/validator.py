import json
import re


def validate_response(response: str):

    # Remove markdown code fences
    response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        jobs = json.loads(response)

        if isinstance(jobs, dict):
            jobs = [jobs]

        return jobs

    except json.JSONDecodeError:
        pass

    # Extract the first JSON array from the response
    
    match = re.search(r"\[[\s\S]*?\]", response)

    if match:
        try:
            jobs = json.loads(match.group())

            if isinstance(jobs, dict):
                jobs = [jobs]

            return jobs

        except json.JSONDecodeError:
            pass

    print("😔 Invalid JSON returned by LLM")
    print("=" * 80)
    print(response[:500])   
    print("=" * 80)

    return []