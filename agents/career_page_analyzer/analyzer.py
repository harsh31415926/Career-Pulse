from .detector import (
    detect_ats,
    has_job_links,
    has_apply_links,
    javascript_required
)


def analyze_career_page(context):

    company = context["company"]

    career_url = context["career_url"]

    html = context["html"]

    ats = detect_ats(html)

    job_links = has_job_links(html)

    apply_links = has_apply_links(html)

    js_required = javascript_required(html)

    analysis = {

        "company": company,

        "ats": ats,

        "career_platform": ats,

        "jobs_embedded": False,

        "job_links_present": job_links,

        "apply_links_present": apply_links,

        "javascript_required": js_required,

        "pagination": False,

        "api_detected": False,

        "strategy": "",

        "recommended_strategy": ""

    }

    if ats == "Greenhouse":

        analysis["strategy"] = "greenhouse"

        analysis["recommended_strategy"] = (
            "Use the Greenhouse extractor."
        )

    elif ats == "Lever":

        analysis["strategy"] = "lever"

        analysis["recommended_strategy"] = (
            "Use the Lever extractor."
        )

    elif ats == "Workday":

        analysis["strategy"] = "workday"

        analysis["recommended_strategy"] = (
            "Use the Workday extractor."
        )

    elif job_links:

        analysis["strategy"] = "follow_links"

        analysis["recommended_strategy"] = (
            "Follow each job link using Playwright."
        )

    else:

        analysis["strategy"] = "parse_current_page"

        analysis["recommended_strategy"] = (
            "Extract jobs directly from the current page."
        )

    context["analysis"] = analysis

    return context

# '''===== TRY ====='''

# from agents.html_processor.loader import load_data
# from agents.career_page_analyzer.analyzer import analyze_career_page

# html = load_data(
#     "outputs/comapnies_front_page_html/Google.html"
# )

# analysis = analyze_career_page(
#     "Google",
#     html
# )


# analysis = analyze_career_page(
#     "Google",
#     html
# )

# print(analysis)