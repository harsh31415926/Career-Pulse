from agents.follow_links_extractor.extractor import extract_links


def route(context):

    strategy = context["analysis"]["strategy"]

    if strategy == "follow_links":

        return extract_links(context)

    elif strategy == "greenhouse":

        print("Greenhouse extractor not implemented.")

    elif strategy == "lever":

        print("Lever extractor not implemented.")

    elif strategy == "workday":

        print("Workday extractor not implemented.")

    else:

        print("Current page extractor not implemented.")

    return context