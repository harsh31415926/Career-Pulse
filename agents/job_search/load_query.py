import json

def load_queries():

    with open('outputs/search_queries.json' , 'r') as f:
        return json.load(f)

all_queries = load_queries()
# print(all_queries)

queries = load_queries()

for query in queries['queries'] :
    print(query)