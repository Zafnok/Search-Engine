import sys
import WebCrawler
from requests.exceptions import SSLError
from urllib.error import URLError

"""
Author: Nicholas Wentz
This script runs the WebCrawler.py until the user inputs a KeyboardInterrupt (Ctrl+C) - should run in cmd/terminal
"""
if __name__ == "__main__":
    try:
        while True:
            try:
                WebCrawler.crawl()
            except SSLError or URLError:
                continue

    except KeyboardInterrupt:
        sys.exit()
