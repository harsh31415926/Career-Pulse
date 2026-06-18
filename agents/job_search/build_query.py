def generate_query(search_profile):

    roles = search_profile['bestTargetRoles']
    locations = search_profile['preferredLocations']

    queries = []

    for role in roles:
        for loc in locations:
            queries.append(f'{role} {loc}')

    
    keywords = search_profile['searchKeywords']

    for key in keywords:
        for loc in locations:
            queries.append(f'{key} {loc}')

    return {'queries' : list(set(queries))}

