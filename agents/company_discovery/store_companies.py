import json

from agents.company_discovery.agent import discover_companies


with open('outputs/search_profile.json' , 'r') as f:
    search_profile = json.load(f)


companies = discover_companies(search_profile)


companies = (
    companies
    .replace("```json","")
    .replace("`","")
    .strip()
)

# print(type(companies))  <str>

companies_json = json.loads(companies)

# print(type(companies_json))  <dict>



with open('outputs/target_companies.json', 'w') as f :
    json.dump(companies_json , f , indent=4)



print('Companies added successfully ...........')
