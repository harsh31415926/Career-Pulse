from bs4 import BeautifulSoup

def detect_ats(html: str):

    html = html.lower()

    if "greenhouse.io" in html:
        return "Greenhouse"

    if "jobs.lever.co" in html:
        return "Lever"

    if "ashbyhq.com" in html:
        return "Ashby"

    if "myworkdayjobs.com" in html:
        return "Workday"

    if "smartrecruiters.com" in html:
        return "SmartRecruiters"

    return "Custom"







''' ====================== JOB LINKS ========================= '''

from bs4 import BeautifulSoup

def has_job_links(html):

    soup = BeautifulSoup(html, "html.parser")

    for a in soup.find_all("a", href=True):

        href = a["href"].lower()

        if any(word in href for word in [
            "job",
            "career",
            "position",
            "opening"
        ]):
            return True

    return False




''' ====================== APPLY LINKS ========================= '''

def has_apply_links(html):

    return "apply" in html.lower()


''' ====================== JAVASCRIPT ========================= '''

def javascript_required(html):

    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all("script")

    return len(scripts) > 10

