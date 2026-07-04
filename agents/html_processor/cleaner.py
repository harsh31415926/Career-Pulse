# this agent is taking the html and reading it a lil

from bs4 import BeautifulSoup

def clean_html(html):

    soup = BeautifulSoup(html , "html.parser")

    return soup.get_text(separator='\n', strip=True)    