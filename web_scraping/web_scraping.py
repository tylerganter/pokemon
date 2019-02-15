#!/usr/bin/env python
"""

Web Service API: request from a webpage to get info
(may need authorization key)

"""
import sys
from abc import ABCMeta, abstractmethod
from urlparse import urlsplit
import re
from collections import deque

from bs4 import BeautifulSoup
import requests


class _CrawlerProcessor():
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, page):
        '''asdf'''
        pass


class GetLinks(_CrawlerProcessor):
    def __init__(self):
        self.links = set()

    def process(self, page):
        new_links = re.findall(b'href="(http[s]?://.*?)"', page.content)

        for new_link in new_links:
            self.links.add(new_link)


class GetEmailAddresses(_CrawlerProcessor):
    def __init__(self):
        self.email_addresses = set()

    def process(self, page):
        new_email_addresses = re.findall(
            r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", page.text, re.I
        )

        for new_email_address in new_email_addresses:
            self.email_addresses.add(new_email_address)


def crawl(initial_url, processor=None, max_num_links=1, same_base=1):
    """
    crawl the web starting from the provided initial URL

    :param initial_url: URL link (string)
    :param processor: a processor object. This object should have a .process(response) function
    :param max_num_links: the maximum number of links to be crawled (1 -> only the initial URL)
    :param same_base: valid values:
                    0 - same exact netloc:
                        example: if the initial URL is 'docs.python.org' all followed links must be of the same format
                    1 - same base url excluding pre-pending parts
                        example: if the initial URL is 'docs.python.org' all links of format 'python.org' are valid
                    2 - not the same base, follow any links found
    :return:
    """
    # TODO understand how to get unicode (voxel51.com)
    # TODO try something that doesn't support https but don't provide the schema

    if same_base == 0:
        initial_url_base = urlsplit(initial_url).netloc
    elif same_base == 1:
        initial_url_base = urlsplit(initial_url).netloc

        # strip all parts before the final 'exampleurl.specifier'
        # examples:
        #       www.python.org -> python.org
        #       docs.python.org -> python.org
        initial_url_base = '.'.join(initial_url_base.split('.')[-2:])
    elif same_base == 2:
        user_response = raw_input('same_base=2! This means that any links found will be followed.\n'
                                  'Are you sure you want to proceed? y/n: ')
        if user_response != 'y':
            sys.exit('Exiting: next time set same_base to 0 or 1')
    else:
        if not isinstance(same_base, int):
            raise TypeError
        else:
            raise ValueError

    # add schema if necessary
    initial_url = urlsplit(initial_url, scheme='https').geturl()  # TODO why is this adding 3 slashes?

    # a queue of urls to be crawled
    new_urls = deque([initial_url])

    # a set of urls that we have already crawled
    processed_urls = set()

    # process urls one by one until we exhaust the queue
    while len(new_urls) > 0 and len(processed_urls) < max_num_links:
        # move next url from the queue to the set of processed urls
        url = new_urls.popleft()
        processed_urls.add(url)

        # extract base url and path to resolve relative links
        parts = urlsplit(url)
        base_url = '{0.scheme}://{0.netloc}'.format(parts)
        # path = url[:url.rfind('/') + 1] if '/' in parts.path else url

        # get url's content
        print("Processing %s" % url)
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            # ignore pages with errors
            continue

        # process the response
        if processor is not None and hasattr(processor, 'process'):
            processor.process(response)

        # TODO figure out which one to use
        # create a beautiful soup for the html document
        # soup = BeautifulSoup(response.text)
        # soup = BeautifulSoup(response.text, features='lxml')
        soup = BeautifulSoup(response.text, features='html.parser')

        # find and process all the anchors in the document
        for anchor in soup.find_all('a'):
            # extract link url from the anchor
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''

            # add base url to relative links
            if link.startswith('/'):
                link = base_url + link

            if initial_url_base not in urlsplit(link).netloc:
                # link doesn't share the same base url with the initial url
                continue

            # add the new url to the queue if it's of HTTP protocol, not enqueued and not processed yet
            if link.startswith('http') and not link in new_urls and not link in processed_urls:
                new_urls.append(link)

    return processor, processed_urls


if __name__ == '__main__':
    # url = 'https://www.ableton.com/'
    # url = 'https://www.ableton.com/en/contact-us/'

    # url = 'https://www.python.org/'
    # url = 'http://www.python.org/'
    # url = 'https://python.org/'
    # url = 'https://python.org'

    # url = 'www.python.org/'

    TESTURL = 'https://www.python.org/'
    # url = 'https://docs.python.org/3/'

    # get_links = GetLinks()
    # crawl(url, processor=get_links, max_num_links=10, same_base=1)
    # print('\nResults:')
    # for link in get_links.links:
    #     print(link)

    get_email_addresses = GetEmailAddresses()
    crawl(TESTURL,
          processor=get_email_addresses,
          max_num_links=10, same_base=1)

    print('\nResults:')
    for email in get_email_addresses.email_addresses:
        print(email)
