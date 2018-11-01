import requests
from bs4 import BeautifulSoup
import time
from collections import deque
from requests.compat import urljoin
from SearchEngineCopyCopy import SearchEngine

"""
Author: Nicholas Wentz
Description: This class describes a WebScraper which takes a url, finds all urls on the page, and scrapes each page for 
descriptions, then adds the descriptions' words and sites to the search engine
"""


# TODO rename file
# TODO add functionality to pick up where left off - maybe write the queue to a file
# TODO need to scrape each subsite
# TODO maybe add url as param for init

class WebScraper:
    def __init__(self):
        """
        The constructor sets up the SearchEngine to add tags and sites to, as well as the initial url, site_dict which
        holds the sites already visited - mapped to the time since last visit, as well as the site_queue which holds the
        urls to scrape in a queue, and the BeautifulSoup object for build_queue
        """
        self.search_engine = SearchEngine()
        self.url = 'http://www.virginaustralia.com/au/en/bookings/flights/make-a-booking/'
        self.site_dict = dict()
        self.site_queue = deque()
        self.soup = BeautifulSoup(requests.get(self.url).text,
                                  features="html.parser")  # TODO could probably change to build_queue function

    def build_queue(self):
        """
        Builds initial site_queue - scrapes soup object for urls and adds them to the site_queue
        :return: None
        """
        for link in self.soup.find_all('a'):
            if link.has_attr('href'):
                other_url = urljoin(self.url, link['href'])
                if ((other_url not in self.site_dict and other_url not in self.site_queue) or (
                        other_url in self.site_dict and self.site_dict[other_url] > 86400)):
                    self.site_queue.append(other_url)

    def scrape(self):
        """
        Dequeues the site_queue, then looks in that site for the description, adds each word to the search engine
        dictionary as the tag with the site as the data. Additionally adds each site to the site_dict with the time since
         last search
        :return:
        """
        site = self.site_queue.popleft()
        print(site, self.search_engine.search_dictionary)
        soup = BeautifulSoup(requests.get(site).text, features="html.parser")
        for meta in soup.find_all('meta'):
            if 'name' in meta.attrs and meta.attrs['name'] == 'description':
                self.search_engine.add_to_dictionary(meta.attrs['content'].split(), site)
                self.site_dict[site] = time

# TODO look at title, desc, keywords, content, etc use NTLK?
# while len(site_queue) > 0:
# print[meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
