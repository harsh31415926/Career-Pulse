import json


def save_jobs(all_jobs):

    with open(
        "outputs/jobs.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_jobs,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"Saved {len(all_jobs)} jobs.")