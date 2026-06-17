import json

from agents.profile_builder.agent import build_profile

with open("outputs/candidate_profile.json", "r") as f:

    candidate = json.load(f)

profile= build_profile(candidate)
# print(profile)

profile = profile.replace("```json","").replace("`","").strip()


with open("outputs/search_profile.json" , "w") as f :
    f.write(profile)
