import json

def save_jobs(jobs):
    with open("outputs/jobs.json","w") as f:
        json.dump(jobs,f,indent=4)

