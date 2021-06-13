from bs4 import BeautifulSoup
import requests


def url_to_soup(url, parser="lxml"):
    # pull the webpage
    response = requests.get(url)

    return BeautifulSoup(response.text, features=parser)


def file_to_soup(filepath, parser="lxml"):
    with open(filepath) as f:
        BeautifulSoup(f.read(), features=parser)
