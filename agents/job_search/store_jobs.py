# agents/job_search/store_jobs.py

import json

def save_jobs(jobs):
    with open("outputs/jobs.json","w") as f:
        json.dump(jobs,f,indent=4)

