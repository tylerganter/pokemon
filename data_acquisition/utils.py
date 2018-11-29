"""

"""

from __future__ import absolute_import, division, print_function

import requests
from bs4 import BeautifulSoup

__all__ = ['url_to_soup', 'file_to_soup']

def url_to_soup(url, parser='lxml'):
    # pull the webpage
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema,
            requests.exceptions.ConnectionError) as err:
        raise(err)

    # parse
    soup = BeautifulSoup(response.text, features=parser)

    return soup

def file_to_soup(filepath, parser='lxml'):
    f = open(filepath)

    soup = BeautifulSoup(f.read(), features=parser)

    return soup
