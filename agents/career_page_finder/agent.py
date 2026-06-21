# KNOWN_CAREER_PAGES = {
    
# }

from .known_career_pages import KNOWN_CAREER_PAGES

def find_career_pages(companies):

    result = []

    for company in companies:
        company = company.strip()

        if company in KNOWN_CAREER_PAGES:
            result.append(
                {
                    'company': company, 
                    'career_url' : KNOWN_CAREER_PAGES[company]
                }
            )
    
    return result

# print(find_career_pages(["Google"]))
