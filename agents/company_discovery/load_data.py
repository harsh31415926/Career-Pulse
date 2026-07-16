import json


COMPANIES_FILE = "outputs/company_career.json"


def load_companies():

    with open(
        COMPANIES_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        companies = json.load(f)

    return companies