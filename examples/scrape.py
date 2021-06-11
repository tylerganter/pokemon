"""This is an example of web scraping to get links or email addresses.

@todo(Tyler) use Scrapy web scraper framework
  https://docs.scrapy.org/en/latest/intro/tutorial.html
"""

from pprint import pprint
from pokemon.web.scrape import GetEmailAddresses, crawl


if __name__ == '__main__':
    # url = 'https://www.ableton.com/'
    # url = 'https://www.ableton.com/en/contact-us/'

    # url = 'https://www.python.org/'
    # url = 'http://www.python.org/'
    # url = 'https://python.org/'
    # url = 'https://python.org'

    # url = 'www.python.org/'

    # url = 'https://www.python.org/'
    url = 'https://docs.python.org/3/'

    # get_links = GetLinks()
    # crawl(url, processor=get_links, max_num_links=10, same_base=1)
    # print('\nResults:')
    # for link in get_links.links:
    #     print(link)

    get_email_addresses = GetEmailAddresses()
    processor, processed_urls = crawl(url, processor=None, max_num_links=10, same_base=1)
    pprint(processed_urls)
    # print('\nResults:')
    # for email in get_email_addresses.email_addresses:
    #     print(email)
