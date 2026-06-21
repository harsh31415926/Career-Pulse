import json

from agents.career_page_finder.agent import find_career_pages

with open('outputs/target_companies.json' , 'r') as f :
    companies_data = json.load(f)

# print(companies_data)

companies = []

companies = companies_data["companies"]

career_pages = find_career_pages(companies)
# print(career_pages)


with open('outputs/company_career.json' , 'w') as f :

    json.dump(career_pages, f, indent = 4)
    print("Career Pages added successfully 😌 ")