import sys
import WebScraper

if __name__ == "__main__":
    try:
        while True:
            WebScraper.scrape()
    except KeyboardInterrupt:
        sys.exit()
