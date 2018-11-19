import sys
import WebScraper

# import gc

if __name__ == "__main__":
    try:
        x = 1
        while True:
            WebScraper.scrape()
            # gc.collect()

    except KeyboardInterrupt:
        sys.exit()
