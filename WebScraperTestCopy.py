import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import deque
from requests.compat import urljoin
from SearchEngine import SearchEngine
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Site import Site
import yaml
import atexit

# TODO may not need JS, the reason JavaScript is not enabled displays is because that is the first webpage - if don't
# TODO need JS, then remove selenium stuff (may just remove whole Copy.py)
# TODO maybe try running on Pi overnight
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
        self.options = Options()
        self.options.add_argument("--headless")  # no gui
        self.options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome("chromedriver.exe", chrome_options=self.options)
        self.driver.implicitly_wait(20)
        self.loaded = self.populate_from_file(file_name)
        if self.loaded and len(self.site_queue) > 1:
            self.url = self.site_queue.popleft()
        atexit.register(self.write_to_file, file_name)
        self.soup = BeautifulSoup(requests.get(self.url).text,
                                  features="html.parser")  # TODO could probably change to build_queue function

    @staticmethod
    def visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]'] or isinstance(element,
                                                                                                           Comment):
            return False
        return True

    def build_queue(self):
        """
        Builds initial site_queue - scrapes soup object for urls and adds them to the site_queue
        :return: None
        """
        for link in self.soup.find_all('a', href=True):  # if this doesn't work anymore, delete href=True
            # TODO add above line changes to main Scraper file
            # if link.has_attr('href'): TODO should be good to remove
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
        self.driver.get(site)
        # print(self.driver.page_source)
        soup = BeautifulSoup(self.driver.find_element_by_tag_name("html").get_attribute("innerHTML"),
                             # TODO can remove all the get attribute stuff IF JS not needed
                             features="html.parser")
        # soup = BeautifulSoup(requests.get(site, headers={
        #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}).text,
        #                      features="html.parser")  # TODO we have detected that your browser is not javascript enabled
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
        new_site = Site(site_name=site, relevancy_dictionary=site_relevancy_dictionary)
        SearchEngine.add_to_search_dictionary(site_relevancy_dictionary.keys(), new_site)
        # print(u" ".join(self.search_engine.clean_string(text) for text in
        #                 visible_texts))  # u is for unicode

        # self.search_engine.site_dictionary(site, Site())
        # self.search_engine.add_to_search_dictionary(meta.attrs['content'].split(), site)
        # self.site_dict[site] = time

        # TODO look at title, desc, keywords, content, etc use NTLK?
        # while len(site_queue) > 0:
        # print[meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]

    def write_to_file(self, file_name):
        try:
            with open(file_name, 'x+') as data_file:
                yaml.dump(self.site_queue, data_file)
        except FileExistsError:
            with open(file_name, 'w') as data_file:
                yaml.dump(self.site_queue, data_file)

    def populate_from_file(self, file_name):
        try:
            with open(file_name, 'r') as data_file:
                self.site_queue = yaml.load(data_file)
            return True
        except FileNotFoundError:
            return False
