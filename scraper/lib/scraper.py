# Scrapes the data from parent_url 
# and stores into seperate data/data.csv
#
# url : url link to an ad page
#
# TODO:
# remove bad urls from urls       X
# make it only scrape new urls    X
# make a safety copy of data.csv  X
# add progress bars               X
# implement time log              X
# use pickles
# circle user agent
# cache requests ?
# make data_backup.csv immutable

import os
import re
import pandas as pd
import requests
import subprocess

from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime

from lib.preprocess import Preprocess
from lib.parser import Parser


# Supress Warnings
import warnings
def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter(action='ignore')
    fxn()
warnings.simplefilter("ignore", category=FutureWarning)


class Scraper:
    def __init__(self, cwd, parent_url):
        self.parent_url = parent_url

        self.CWD = cwd
        self.LOGFILE = os.path.abspath(os.path.join(self.CWD, 'log.txt'))
        self.URLFILE = os.path.abspath(os.path.join(self.CWD, 'urls.txt'))
        self.DATA_DIR = os.path.abspath(os.path.join(self.CWD,  '../data'))

        if not os.path.exists(self.DATA_DIR):
            os.mkdir(self.DATA_DIR)


    def get_response(self, page=None, url=None):
        # Requests and returns webpage html

        if url != None:
            got = requests.get(url=url)
            if (got.status_code == 200):
                return got.text
            else:
                return False

        else:
            url = f"{self.parent_url}/category/katoikies?pref=1&page={page}&ads-per-page=100"
            got = requests.get(url=url)
            got.raise_for_status()
            if (got.status_code == 200):
                return got.text
            else:
                return False


    def get_urls(self):
        # Returns all urls to ad pages

        try: 
            urls = [line.strip() for line in open(self.URLFILE, 'r')]
        except:
            urls = []

        new_urls = []
        page = 1

        print('Getting urls...')

        while True:
            response = self.get_response(page)
            soup = BeautifulSoup(response, 'html.parser')
            articles = soup.find_all('article', class_=re.compile('classi-list-item.*'))

            for article in articles:
                url = self.parent_url + article.find('div', class_='classi-list-item-body').find('a', class_='image-content')['href']
                if url not in urls:
                    new_urls.append(url)
                    urls.append(url)

            page += 1
            print(f'{page*100}', end='\r')

            if not articles:    # list is empty -> end reached
                print(f'Got {len(new_urls)} new url links.')
                break

        self.log(f'Got {len(new_urls)} new urls.')
        return new_urls


    def scrape_urls(self, urls):         
        # main scraping and storing method

        count = 0
        preprocess = Preprocess()
        parser = Parser()

        progress_bar = tqdm(range(len(urls)), 
                            desc='Scraping',
                            total=None,
                            smoothing=1.0
                            )

        # Read csv file
        try:
            df = pd.read_csv(f'{self.DATA_DIR}/data.csv')
        except:
            df = pd.DataFrame()

        # Iterate urls and scrape
        for _, url in zip(progress_bar, urls):
            ad = self.get_response(page=None, url=url)
            if ad == False :
                continue

            try:
                soup = BeautifulSoup(ad, 'html.parser')
            except Exception as e:
                continue

            # Parse html data
            attrs = parser.parse(soup)
            # Preprocess data
            attrs = preprocess.preprocess(attrs)
            if attrs == False:
                continue

            # Append data to Dataframe
            try:
                df2 = pd.DataFrame([attrs])
                df = pd.concat([df, df2], ignore_index=True)
                count += 1
            except Exception as e: 
                print(e)
                continue

        # Drop entities with identical IDs
        df = df.drop_duplicates(subset='code')

        # Save to file
        df.to_csv(f'{self.DATA_DIR}/data.csv', index=False)
        self.write_to_disk(urls)

        # Log
        message = f"Scraped {count} entities."
        print(message)
        self.log(message)
        self.notify(message)


    def log(self, message):
        # Print to log.txt
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')
        with open(self.LOGFILE, 'a') as log:
            log.write(f'{timestamp} : {message}\n')

    def notify(self, message):
        try:
            subprocess.Popen(['notify-send', 'rent-dion', message])
        except:
            pass


    def write_to_disk(self, urls):
        # Write urls to urls.txt
        with open(self.URLFILE, 'a') as f:
            for item in urls:
                f.write(f'{item}\n')


    def safety_copy(self):
        # Make a safety copy of data.csv
        try:
            df = pd.read_csv(f'{self.DATA_DIR}/data.csv')
        except:
            return

        df.to_csv(f'{self.DATA_DIR}/data_backup.csv', index=False)
