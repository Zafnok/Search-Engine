import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from requests.compat import urljoin
import NoSQLdb
import SearchEngine
from collections import Counter
import time
import FileQueue

"""
Author: Nicholas Wentz
Description: This class describes a WebScraper which takes a url, finds all urls on the page, and scrapes each page for 
descriptions, then adds the descriptions' words and sites to the search engine
"""


# TODO add robots.txt stuff
# TODO rename file
# TODO add functionality to pick up where left off - maybe write the queue to a file
# TODO need to scrape each subsite - think done
# TODO maybe add url as param for init
# TODO add threading to make faster
def visible(element):
    """
    This function takes an element and checks whether it is visible or not
    :param element: Element to check whether visible or not
    :return: Whether the element is in the visible elements
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]'] \
            or isinstance(element, Comment):
        return False
    return True


# TODO might be able to become static class

def build_queue(url):
    """
    Builds initial site_queue - scrapes soup object for urls and adds them to the site_queue
    :return: None
    """

    for link in BeautifulSoup(requests.get(url).text, features="html.parser").find_all('a', href=True):
        other_url = urljoin(url, link['href'])
        if (not NoSQLdb.exists_in_site_db(other_url) or (NoSQLdb.exists_in_site_db(other_url) and time.time()
                                                         - NoSQLdb.retrieve_kv_site_db_time(other_url) > 86400)):
            FileQueue.enqueue(other_url)


def scrape():
    """
    Dequeues the site_queue, then looks in that site for the description, adds each word to the search engine
    dictionary as the tag with the site as the data. Additionally adds each site to the site_dict with the time since
     last search
    :return:
    """
    site = FileQueue.dequeue()
    site = site if site is not None else "https://en.wikipedia.org/wiki/Philosophy"
    print(site)
    build_queue(site)  # TODO need to make it so that queue doesn't keep getting bigger and no progress made -
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
    visible_texts = list(filter(visible, texts))
    count = Counter([SearchEngine.clean_string(word) for text in visible_texts for word in text.split()])
    count = {key: value for key, value in count.items() if not (len(key) == 0 or key.isspace())}
    for key, value in count.items():
        if key in site_relevancy_dictionary:
            site_relevancy_dictionary[key] += SearchEngine.search_ranking_algorithm(value)
        else:
            site_relevancy_dictionary[key] = SearchEngine.search_ranking_algorithm(value)
    NoSQLdb.store_multiple_kv_search_db([*site_relevancy_dictionary], site)
    NoSQLdb.store_kv_site_db(site, [time.time(), site_relevancy_dictionary])
    # site_relevancy_dictionary.clear()

# def write_to_file(self, file_name):
#     """
#     This function dumps the queue to a YAML file
#     :param file_name: YAML file to dump queue to
#     :return: None
#     """
#     try:
#         with open(file_name, 'x+') as data_file:
#             yaml.dump(self.site_queue, data_file)
#     except FileExistsError:
#         with open(file_name, 'w') as data_file:
#             yaml.dump(self.site_queue, data_file)
#
# def populate_from_file(self, file_name):
#     """
#     This functions reads a YAML file into the site queue
#     :param file_name: YAML file to read from
#     :return: None
#     """
#     try:
#         with open(file_name, 'r') as data_file:
#             self.site_queue = yaml.load(data_file)
#         return True
#     except FileNotFoundError:
#         return False
