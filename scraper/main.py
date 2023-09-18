import os
from lib.scraper import Scraper


if __name__ == '__main__':

    path = os.getcwd()
    parent_url = 'https://www.kritikes-aggelies.gr'

    scraper = Scraper(path, parent_url)

    # Scrape Urls
    new_urls = scraper.get_urls()

    # Make a safety copy
    scraper.safety_copy()

    # Scrape and Save Data from urls
    scraper.scrape_urls(new_urls)
