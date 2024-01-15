import os
from lib.scraper import Scraper

if __name__ == '__main__':

    parent_url = 'https://www.kritikes-aggelies.gr'
    path = os.path.dirname(os.path.realpath(__file__))

    scraper = Scraper(path, parent_url)

    # Scrape urls
    new_urls = scraper.get_urls()

    # Make a safety copy
    scraper.safety_copy()

    # Scrape and Save Data from urls
    scraper.scrape_urls(new_urls)
