import json

def load_companies():

    with open('outputs/company_career.json' , 'r') as f:
        return json.load(f)
    
