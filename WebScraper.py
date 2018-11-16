import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import deque
from requests.compat import urljoin
import NoSQLdb
import SearchEngine
from collections import Counter
import yaml
import atexit
import time

"""
Author: Nicholas Wentz
Description: This class describes a WebScraper which takes a url, finds all urls on the page, and scrapes each page for 
descriptions, then adds the descriptions' words and sites to the search engine
"""


# TODO rename file
# TODO add functionality to pick up where left off - maybe write the queue to a file
# TODO need to scrape each subsite - think done
# TODO maybe add url as param for init
# TODO add threading to make faster
class WebScraper:
    def __init__(self, file_name="web_scraper_data_file.yaml"):
        """
        The constructor sets up the SearchEngine to add tags and sites to, as well as the initial url, site_dict which
        holds the sites already visited - mapped to the time since last visit, as well as the site_queue which holds the
        urls to scrape in a queue, and the BeautifulSoup object for build_queue
        """
        self.url = "https://www.virginaustralia.com/au/en/bookings/flights/make-a-booking/"
        self.site_dict = dict()
        self.site_queue = deque()
        self.file_name = file_name
        self.populate_from_file(file_name)
        atexit.register(self.write_to_file, file_name)

    @staticmethod
    def visible(element):
        """
        This function takes an element and checks whether it is visible or not
        :param element: Element to check whether visible or not
        :return: Whether the element is in the visible elements
        """
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]'] or isinstance(element,
                                                                                                           Comment):
            return False
        return True

    # TODO might be able to become static class
    def build_queue(self, url):
        """
        Builds initial site_queue - scrapes soup object for urls and adds them to the site_queue
        :return: None
        """

        for link in BeautifulSoup(requests.get(url).text, features="html.parser").find_all('a', href=True):
            other_url = urljoin(url, link['href'])
            if ((other_url not in self.site_dict and other_url not in self.site_queue) or (
                    other_url in self.site_dict and self.site_dict[other_url] > 86400)):
                self.site_dict[other_url] = time.time()
                self.site_queue.append(other_url)

    def scrape(self):
        """
        Dequeues the site_queue, then looks in that site for the description, adds each word to the search engine
        dictionary as the tag with the site as the data. Additionally adds each site to the site_dict with the time since
         last search
        :return:
        """
        site = self.site_queue.popleft()
        print(site)
        self.build_queue(site)  # TODO need to make it so that queue doesn't keep getting bigger and no progress made -
        # TODO ordering of queue somehow? - queue is FIFO so maybe no big deal...
        soup = BeautifulSoup(requests.get(site).text,
                             features="html.parser")  # TODO we have detected that your browser is not javascript enabled
        site_relevancy_dictionary = dict()
        for meta in soup.find_all('meta'):
            if 'name' in meta.attrs:
                if meta.attrs['name'] == 'keywords':
                    count = Counter([SearchEngine.clean_string(word) for word in meta.attrs['content'].split()])
                    for key, value in count.items():
                        if key in site_relevancy_dictionary:
                            site_relevancy_dictionary[key] += 2 * SearchEngine.search_ranking_algorithm(value)
                        else:
                            site_relevancy_dictionary[key] = 2 * SearchEngine.search_ranking_algorithm(value)

                if meta.attrs['name'] == 'description':
                    # TODO make Site object using site_relevancy_dictionary and algorithm, add in content and keywords
                    # TODO then make search engine dictionary be the string which is the key for the site dictionary in
                    # TODO search engine - should reduce space reqs? or maybe it is just a pointer so it wouldn't
                    # TODO necessarily
                    count = Counter([SearchEngine.clean_string(word) for word in meta.attrs['content'].split()])
                    for key, value in count.items():
                        if key in site_relevancy_dictionary:
                            site_relevancy_dictionary[key] += SearchEngine.search_ranking_algorithm(value)
                        else:
                            site_relevancy_dictionary[key] = SearchEngine.search_ranking_algorithm(value)
        for key in site_relevancy_dictionary.keys():
            site_relevancy_dictionary[key] = pow(site_relevancy_dictionary[key], 2)
        texts = soup.findAll(text=True)
        visible_texts = filter(self.visible, texts)
        count = Counter([SearchEngine.clean_string(word) for word in
                         (u" ".join(SearchEngine.clean_string(text) for text in
                                    visible_texts).split())])
        count = {key: value for key, value in count.items() if not (len(key) == 0 or key.isspace())}
        for key, value in count.items():
            if key in site_relevancy_dictionary:
                site_relevancy_dictionary[key] += SearchEngine.search_ranking_algorithm(value)
            else:
                site_relevancy_dictionary[key] = SearchEngine.search_ranking_algorithm(value)
        NoSQLdb.store_multiple_kv_search_db(site_relevancy_dictionary.keys(), site)
        NoSQLdb.store_kv_site_db(site, site_relevancy_dictionary)

    def write_to_file(self, file_name):
        """
        This function dumps the queue to a YAML file
        :param file_name: YAML file to dump queue to
        :return: None
        """
        try:
            with open(file_name, 'x+') as data_file:
                yaml.dump(self.site_queue, data_file)
        except FileExistsError:
            with open(file_name, 'w') as data_file:
                yaml.dump(self.site_queue, data_file)

    def populate_from_file(self, file_name):
        """
        This functions reads a YAML file into the site queue
        :param file_name: YAML file to read from
        :return: None
        """
        try:
            with open(file_name, 'r') as data_file:
                self.site_queue = yaml.load(data_file)
            return True
        except FileNotFoundError:
            return False
