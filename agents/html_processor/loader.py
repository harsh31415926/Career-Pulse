def load_data(path):

    with open(path , 'r' , encoding = 'utf-8') as f:
        return f.read()

# html = load_data("/Users/harshsharma/Desktop/AIProject/AgenticAI/Career_pulse/outputs/comapnies_front_page_html/Amazon.html")
# print(html)