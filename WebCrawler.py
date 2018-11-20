import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from requests.compat import urljoin
import NoSQLdb
import SearchEngine
from collections import Counter
import time
import FileQueue
import re
import atexit
import urllib.robotparser
import tldextract
from urllib.parse import urlsplit

"""
Author: Nicholas Wentz
Description: This class describes a WebCrawler which takes a url, finds all urls on the page, and scrapes each page for 
descriptions, then adds the descriptions' words and sites to the search engine
"""

atexit.register(NoSQLdb.close_and_save)
robot_parser = urllib.robotparser.RobotFileParser()


# TODO add sitemaps.xml stuff
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


def build_queue(url):
    """
    Builds initial site_queue - scrapes soup object for urls and adds them to the site_queue
    :return: None
    """

    for link in \
            BeautifulSoup(requests.get(url, verify=
            r"C:\Users\Zafno\AppData\Local\Programs\Python\Python37\lib\site-packages\certifi\cacert.pem").text,
                          # this is a path to an SSL certificate, since I kept getting SSL errors
                          features="html.parser").find_all('a', href=re.compile(r"^[^#]")):
        other_url = urljoin(url, link['href'])
        if (not NoSQLdb.exists_in_site_db(other_url) or (NoSQLdb.exists_in_site_db(other_url) and time.time()
                                                         - NoSQLdb.retrieve_kv_site_db_time(other_url) > 86400)):
            FileQueue.enqueue(other_url)


def crawl():
    """
    Dequeues the site_queue, then looks in that site for the description, adds each word to the search engine
    dictionary as the tag with the site as the data. Additionally adds each site to the site_dict with the time since
     last search
    :return:
    """
    site = FileQueue.dequeue()
    site = site if site is not None else "https://en.wikipedia.org/wiki/Philosophy"
    extract = tldextract.extract(site)
    scheme = urlsplit(site).scheme
    root_domain = "{}://{}.{}".format(scheme, extract.domain, extract.suffix)
    robots_txt = urljoin(root_domain, "robots.txt")
    robot_parser.set_url(robots_txt)
    robot_parser.read()
    rrate = robot_parser.request_rate("*")
    if not NoSQLdb.exists_in_robots_db(root_domain):
        NoSQLdb.store_kv_robots_db(root_domain,
                                   [(rrate.requests if rrate is not None else None,
                                     rrate.seconds if rrate is not None else None), [-1, -1, -1],
                                    robot_parser.crawl_delay("*")])
    if NoSQLdb.can_make_request(root_domain):
        if robot_parser.can_fetch("*", site):
            NoSQLdb.make_request(root_domain)
            content_type = requests.head(site,
                                         verify=r"C:\Users\Zafno\AppData\Local\Programs\Python\Python37\lib\site-packages\certifi\cacert.pem",
                                         allow_redirects=True).headers.get("content-type")
            if content_type[0:content_type.find('/')] == 'text':
                print(site)
                build_queue(
                    site)  # TODO need to make it so that queue doesn't keep getting bigger and no progress made -
                # TODO ordering of queue somehow? - queue is FIFO so maybe no big deal...
                soup = \
                    BeautifulSoup(requests.get(site, verify=
                    r"C:\Users\Zafno\AppData\Local\Programs\Python\Python37\lib\site-packages\certifi\cacert.pem").text,
                                  features="html.parser")  # TODO we have detected that your browser is not javascript enabled
                site_relevancy_dictionary = dict()
                for meta in soup.find_all('meta'):
                    if 'name' in meta.attrs:
                        if meta.attrs['name'] == 'keywords':
                            count = Counter(
                                [SearchEngine.clean_string(word) for word in meta.attrs['content'].split()])
                            for key, value in count.items():
                                if key in site_relevancy_dictionary:
                                    site_relevancy_dictionary[key] += 2 * SearchEngine.search_ranking_algorithm(
                                        value)
                                else:
                                    site_relevancy_dictionary[key] = 2 * SearchEngine.search_ranking_algorithm(
                                        value)

                        if meta.attrs['name'] == 'description':
                            count = Counter(
                                [SearchEngine.clean_string(word) for word in meta.attrs['content'].split()])
                            for key, value in count.items():
                                if key in site_relevancy_dictionary:
                                    site_relevancy_dictionary[key] += SearchEngine.search_ranking_algorithm(
                                        value)
                                else:
                                    site_relevancy_dictionary[key] = SearchEngine.search_ranking_algorithm(
                                        value)
                for key in site_relevancy_dictionary.keys():
                    site_relevancy_dictionary[key] = pow(site_relevancy_dictionary[key], 2)
                texts = soup.findAll(text=True)
                visible_texts = list(filter(visible, texts))
                count = Counter(
                    [SearchEngine.clean_string(word) for text in visible_texts for word in text.split()])
                count = {key: value for key, value in count.items() if not (len(key) == 0 or key.isspace())}
                for key, value in count.items():
                    if key in site_relevancy_dictionary:
                        site_relevancy_dictionary[key] += SearchEngine.search_ranking_algorithm(value)
                    else:
                        site_relevancy_dictionary[key] = SearchEngine.search_ranking_algorithm(value)
                NoSQLdb.store_multiple_kv_search_db([*site_relevancy_dictionary], site)
                NoSQLdb.store_kv_site_db(site, [time.time(), soup.title.string, site_relevancy_dictionary])
                site_relevancy_dictionary.clear()
        else:
            FileQueue.enqueue(site)
    else:
        FileQueue.enqueue(site)
