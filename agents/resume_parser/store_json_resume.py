from agents.resume_parser.llm_parser import llm_parced_resume_text_json

import json

llm_parced_resume_text_json = llm_parced_resume_text_json.replace(
    "```json",
    ""
).replace(
    "```",
    ""
).replace(
    "`",
    ""
).strip()



# print(llm_parced_resume_text_json)
# print(type(llm_parced_resume_text_json))


file_name = input("Name of your JSON file ??\n")

if __name__ == '__main__':
    json_profile = json.loads(llm_parced_resume_text_json)  

    with open(f"outputs/{file_name}.json" , 'w') as f:

        json.dump(json_profile, f, indent = 4)
        print("Profile Saved Successfully")