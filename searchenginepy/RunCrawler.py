import sys
import WebCrawler
from requests.exceptions import SSLError
from urllib.error import URLError

if __name__ == "__main__":
    try:
        x = 1
        while True:
            try:
                WebCrawler.crawl()
            except SSLError or URLError:
                continue

    except KeyboardInterrupt:
        sys.exit()
