import json

from agents.job_search.build_query import generate_query

''' : ============================== Take the profile of the candidate =============================: '''

with open ("outputs/search_profile.json" , "r") as f:
    search_profile = json.load(f)


queries = generate_query(search_profile)


with open ("outputs/search_queries.json" , "w") as f:
    json.dump(queries ,f , indent = 4)

print("succesfully added Queries")
