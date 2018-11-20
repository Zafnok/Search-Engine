import sys
import WebCrawler

# import gc

if __name__ == "__main__":
    try:
        x = 1
        while True:
            WebCrawler.crawl()
            # gc.collect()

    except KeyboardInterrupt:
        sys.exit()
