#!/usr/bin/env python
"""

Web Service API: request from a webpage to get info (may need authorization key)

"""
from abc import ABC, abstractmethod
from collections import deque
import re
import sys
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
import requests

# from lxml import html, etree
# import json

# # Ignore SSL certificate errors
# import ssl
# ctx = ssl.create_default_context()
# ctx.check_hostname = False
# ctx.verify_mode = ssl.CERT_NONE


class _CrawlerProcessor(ABC):
    @abstractmethod
    def process(self, page):
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
    """Crawl the web starting from the provided initial URL

    Args:
        initial_url: URL link
        processor: a processor object. This object should have a .process(response)
            function
        max_num_links: the maximum number of links to be crawled
            (1 -> only the initial URL)
        same_base: valid values:
            0 - same exact netloc:
                example: if the initial URL is 'docs.python.org' all followed links must
                be of the same format
            1 - same base url excluding pre-pending parts
                example: if the initial URL is 'docs.python.org' all links of format
                'python.org' are valid
            2 - not the same base, follow any links found

    Returns:
        TODO
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
        initial_url_base = ".".join(initial_url_base.split(".")[-2:])
    elif same_base == 2:
        # TODO
        raise NotImplementedError("TODO")
    else:
        raise ValueError(f"Invalid value for arg `same_base`: {same_base}")

    # add schema if necessary
    # TODO why is this adding 3 slashes?
    initial_url = urlsplit(initial_url, scheme="https").geturl()

    new_urls = deque([initial_url])
    processed_urls = set()

    # process urls one by one until we exhaust the queue
    while len(new_urls) > 0 and len(processed_urls) < max_num_links:
        # move next url from the queue to the set of processed urls
        url = new_urls.popleft()
        processed_urls.add(url)

        # extract base url and path to resolve relative links
        parts = urlsplit(url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        # path = url[:url.rfind('/') + 1] if '/' in parts.path else url

        # get url's content
        print("Processing %s" % url)
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            # ignore pages with errors
            continue

        # process the response
        if processor is not None and hasattr(processor, "process"):
            processor.process(response)

        # TODO figure out which one to use
        # create a beautiful soup for the html document
        # soup = BeautifulSoup(response.text)
        # soup = BeautifulSoup(response.text, features='lxml')
        soup = BeautifulSoup(response.text, features="html.parser")

        # find and process all the anchors in the document
        for anchor in soup.find_all("a"):
            # extract link url from the anchor
            link = anchor.attrs["href"] if "href" in anchor.attrs else ""

            # add base url to relative links
            if link.startswith("/"):
                link = base_url + link

            if initial_url_base not in urlsplit(link).netloc:
                # link doesn't share the same base url with the initial url
                continue

            # add the new url to the queue if it's of HTTP protocol, not enqueued and
            # not processed yet
            if (
                    link.startswith("http")
                    and not link in new_urls
                    and not link in processed_urls
            ):
                new_urls.append(link)


    return processor, processed_urls
