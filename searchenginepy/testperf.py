# # import requests
# # import time
# #
# # old_time = time.time()
# # requests.get('https://en.wikipedia.org/wiki/Web_scraping')
# # print(time.time() - old_time)
# # from requests.compat import urljoin
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urlsplit, urlunsplit
# import tldextract
# from requests.compat import urljoin
# import urllib.robotparser
#
# robot_parser = urllib.robotparser.RobotFileParser()
#
# # this works just doesn't print to console correctly
# site = "https://www.knowyourmeme.com"
# extract = tldextract.extract(site)
# print(extract)
# scheme = urlsplit(site).scheme
# print(scheme)
# if scheme != "":
#     print("yeet")
#     root_domain = "{}://{}.{}".format(scheme, extract.domain, extract.suffix)
# print(root_domain)
# print(urljoin(root_domain, "robots.txt"))
# robot_parser.set_url(urljoin(root_domain, "robots.txt"))
# robot_parser.read()
# print(robot_parser.request_rate("*"))
# print(robot_parser.can_fetch("*", site))
# # extracted = tldextract.extract(
# #     "https://www.google.com")
# # print("{}.{}".format(extracted.domain, extracted.suffix))
# # split_url = urlsplit(
# #     "https://upload.wikimedia.org/wikipedia/commons/3/3b/Monks_debating_at_Sera_monastery%2C_2013.webm")
# # print(urlunsplit((split_url.scheme, split_url.netloc, "", "", "")))
# # temp = requests.head(
# #     "https://upload.wikimedia.org/wikipedia/commons/3/3b/Monks_debating_at_Sera_monastery%2C_2013.webm",
# #     allow_redirects=True).headers.get("content-type")
# # if temp[0:temp.find('/')] != "text":
# #     print(temp)
# # soup = \
# #     BeautifulSoup(requests.get(
# #         "https://upload.wikimedia.org/wikipedia/commons/3/3b/Monks_debating_at_Sera_monastery%2C_2013.webm", verify=
# #         r"C:\Users\Zafno\AppData\Local\Programs\Python\Python37\lib\site-packages\certifi\cacert.pem"),
# #         features="html.parser")
# # print(soup.get_text())
import os

print(os.path.dirname(__file__))
