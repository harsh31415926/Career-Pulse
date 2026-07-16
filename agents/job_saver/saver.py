import os
import json


OUTPUT_DIR = "outputs/jobs"


def save_jobs(context):

    output_dir = context.get("config", {}).get("jobs_output_dir", OUTPUT_DIR)

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    company = context["company"].replace(" ", "_")

    filename = f"{company}.json"

    filepath = os.path.join(
        output_dir,
        filename
    )

    if not context.get("jobs"):
        context.setdefault("logs", []).append(
            f"No jobs extracted for {context['company']}; no file written."
        )
        print(f"Saved 0 jobs. No file written for {context['company']}.")
        return context

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            context["jobs"],
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"Saved {len(context['jobs'])} jobs.")
    print(filepath)

    context.setdefault("logs", []).append(
        f"Saved {len(context['jobs'])} jobs to {filepath}"
    )
    context.setdefault("metadata", {})["jobs_output_path"] = filepath

    return context
