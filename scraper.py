# Scrapes the data from parent_url 
# and stores into seperate data/data.csv
#
# url : url link to an ad page
#
# TODO: remove bad urls from urls       X
# TODO: make it only scrape new urls    X
# TODO: make a safety copy of data.csv  X
# TODO: add progress bars               X
# TODO: implement time log              X
# TODO: use pickles
# TODO: circle user agent
# TODO: cache requests ?

import re
import os
import pandas as pd
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from io import StringIO
from html.parser import HTMLParser
from datetime import datetime

# Supress Warnings
import warnings
def fxn():
    warnings.warn("deprecated", DeprecationWarning)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()

warnings.simplefilter("ignore", category=FutureWarning)
parent_url = 'https://www.kritikes-aggelies.gr'


def get_response(page=None, url=None):
    # Requests and returns webpage html

    if url != None:
        got = requests.get(url=url)
        if (got.status_code == 200):
            return got.text
        else:
            return False

    else:
        url = f"{parent_url}/category/katoikies?pref=1&page={page}&ads-per-page=100"
        got = requests.get(url=url)
        got.raise_for_status()
        if (got.status_code == 200):
            return got.text
        else:
            return False

def get_urls():
    # Returns all urls to ad pages

    try: 
        urls = [line.strip() for line in open('urls.txt', 'r')]
    except:
        urls = []

    new_urls = []
    page = 1

    print('Getting urls...')

    while True:
        response = get_response(page)
        soup = BeautifulSoup(response, 'html.parser')
        articles = soup.find_all('article', class_=re.compile('classi-list-item.*'))

        for article in articles:
            url = parent_url + article.find('div', class_='classi-list-item-body').find('a', class_='image-content')['href']
            if url not in urls:
                new_urls.append(url)
                urls.append(url)
        page += 1
        print(page*100, end='\r')

        if not articles:    # list is empty -> end reached
            print(f'Got {len(new_urls)} new url links.')
            break

    log(f'Got {len(new_urls)} new urls.')
    return new_urls

class MLStripper(HTMLParser):       # sanitization
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def parse(soup):        
    # Data formatting
    
    # 29 labels
    labels = { 'Κωδ. Αγγελίας': 'code', 'Κωδ. Αναφοράς': 'report_code', 'Τύπος': 'transaction', 
            'Κατηγορία': 'type', 'Περιοχή': 'location',
            'Εμβαδόν': 'area', 'Εμβαδό (τ.μ.):': 'area', 'Τιμή': 'price', 
            'Τιμή / τ.μ': 'price_per_sqm', 'Τύπος Ακινήτου:': 'stone',
            'Είδος γκαρσονιέρας:': 'type_of_type', 'Είδος Κατοικίας:': 'type_of_type',
            'Είδος Μονοκατοικίας:': 'type_of_type', 'Όροφος:': 'floor', 'Υπνοδωμάτια:': 'bedrooms', 
            'Μπάνια:': 'bathrooms', 'WC:': 'wc', 'Τύπος Θέρμανσης:': 'heating', 
            'Δείκτης ενεργειακής απόδοσης:': 'energy_performance_index',
            'Προσανατολισμός:': 'orientation', 'Θέα:': 'view', 
            'Άλλα Χαρακτηριστικά:': 'other','Ανανεώθηκε:': 'upload_date', 
            'Διαθέσιμο από:': 'available_date', 'Δημοσιεύτηκε:': 'upload_date', 'Επισκέψεις:': 'visits',
            'Κατάσταση:': 'condition', 'Έτος κατασκευής:': 'construction_year',
            'Έτος ανακαίνισης:': 'renovation_year'}

    tags1 = list(soup.find_all('td', class_='title value'.split()))
    tags2 = soup.find_all('dl', class_='attribute')
    tags2 = [tag.find_all('dt dd'.split()) for tag in tags2]
    tags2 = [tag for tup in tags2 for tag in tup]                           # flatten list

    tags = tags1 + tags2
    tags = [ strip_tags(str(string)).strip('(,.)€ \n') for string in tags]  # format strings
    tags_zipped = [ (tags[i], tags[i+1]) for i in range(0, len(tags),2)]    # convert to list of tuples

    attrs = dict(tags_zipped)

    for old_key, new_key in labels.items():
        try:
            attrs[str(new_key)] = attrs.pop(str(old_key))
        except:
            pass

    # some more attributes
    attrs['name'] =  strip_tags(str(soup.find('h1')))

    try: 
        attrs['description'] = strip_tags(str(soup.find("div", class_="classi-text mrg-top-md").find_all("p")[1])).strip('  \n').strip('\n').strip('()')
    except: 
        pass

    try:
        attrs['coordinates'] = str( str(soup.find('a',class_='btn btn-secondary')['href']).strip('https://www.google.com/maps/place/').split(',') )
    except:
        pass

    return attrs

def format_area(area):
    # helper function used in preprocess()

    low = float(area.split('-')[0])
    high = float(area.split('-')[1])
    return (low+high)/2

def preprocess(attrs):
    # Drop entities that have no price or area
    if 'price' not in attrs.keys() or 'area' not in attrs.keys():
        return False

    # Negotiable prices
    if 'Συζητήσιμη' in attrs['price'] :
        attrs['negotiable'] = True
        attrs['price']= attrs['price'].replace(' Συζητήσιμη', '')
    else:
        attrs['negotiable'] = False

    # Convert price to float
    try: 
        attrs['price'] = attrs['price'].replace(',', '.')
        attrs['price'] = attrs['price'].replace('.', '')
        attrs['price'] = float(attrs['price'])
    except:
        return False

    # Convert area to float
    try:
        attrs['area'] = attrs['area'].replace(',', '.')
        attrs['area'] = attrs['area'].replace('.', '')

        if "-" in attrs['area']:
            attrs['area'] = format_area(attrs['area'])
        else:
            attrs['area'] = float(attrs['area'])
    except:
        return False

    # Create price_per_sqm if missing
    if 'price_per_sqm' not in attrs:
        try:
            attrs['price_per_sqm'] = attrs['price']/attrs['area']
        except: pass

    # Convert price_per_sqm to float
    try:
        attrs['price_per_sqm'] = attrs['price_per_sqm'].replace('.', '')
        attrs['price_per_sqm'] = attrs['price_per_sqm'].replace(',', '.')
        attrs['price_per_sqm'] = float(attrs['price_per_sqm'])
    except:
        return False

    # Drop entities requesting to rent/buy/trade
    not_accepted = ['Ζήτηση για Ενοικίαση','Ζήτηση για Αγορά', 'Ανταλλαγή']
    if attrs['transaction'] in not_accepted:
        return False

    # Some entries with 'transaction' == 'Πώληση' (Sale) have price formatted in powers of 3. 
    # e.g: 250 -> 250000. 
    # To identify these cases, we check if  price_per_sqm * area == price
    if attrs['price_per_sqm'] * attrs['area'] - attrs['price'] > 10 :
        attrs['price'] *= 10
    elif attrs['price_per_sqm'] * attrs['area'] - attrs['price'] > 100 :
        attrs['price'] *= 100
    elif attrs['price_per_sqm'] * attrs['area'] - attrs['price'] > 1000 :
        attrs['price'] *= 1000

    # Format floor to floats
    try:
        replace = {'Ισόγειο': 0, 'Ημιώροφος': 0.5, 'Ημιυπόγειο': -0.5, 'Υπερυψωμένο': 0}
        if attrs['floor'] in replace.keys():
            attrs['floor'] = replace[attrs['floor']]
        attrs['floor'] = attrs['floor'].replace('ος', '')
        attrs['floor'] = float(attrs['floor'])
    except:
        pass

    # Format datetime columns: upload_date, renovation_year, 
    # construction_year, available_date
    dates = {'Δευτέρα': 'Monday', 'Τρίτη': 'Tuesday', 'Τετάρτη': 'Wednesday', 
            'Πέμπτη': 'Thursday', 'Παρασκευή': 'Friday', 'Σάββατο': 'Saturday', 'Κυριακή': 'Sunday',
            'Ιαν': 'Jan', 'Φεβ': 'Feb', 'Μαρ': 'Mar', 'Απρ': 'Apr', 'Μαη': 'May', 
            'Ιουν': 'Jun', 'Ιουλ': 'Jul', 'Αυγ': 'Aug', 'Σεπ':'Sep', 'Οκτ': 'Oct', 'Νοε':'Noe', 'Δεκ': 'Dec'}

    today = datetime.today().strftime('%A %-d %b %Y')

    try:
        for key,value in dates.items():
            attrs['upload_date'] = attrs['upload_date'].replace(key, value)
        attrs['upload_date'] = attrs['upload_date'].replace(',', '')
        attrs['upload_date'] = attrs['upload_date'].replace('σήμερα', today)
        date_object = datetime.strptime(attrs['upload_date'], '%A %d %b %Y')
        attrs['upload_date'] = date_object
    except: pass

    try:
        attrs['renovation_year'] = re.sub('[^0-9.-]', '', attrs['renovation_year'])
        year_object = datetime.strptime(attrs['renovation_year'], '%Y')
        attrs['renovation_year'] = year_object
    except: pass

    try:
        attrs['construction_year'] = re.sub('[^0-9.-]', '', attrs['construction_year'])
        year_object = datetime.strptime(attrs['construction_year'], '%Y')
        attrs['construction_year'] = year_object
    except: pass

    try:
        date_object = datetime.strptime(attrs['available_date'], '%d/%b/%Y')
        attrs['available_date'] = date_object
    except: 
        try:
            date_object = datetime.strptime(attrs['available_date'], '%b/%Y')
            attrs['available_date'] = date_object
        except:
            try:
                date_object = datetime.strptime(attrs['available_date'], '%Y')
                attrs['available_date'] = date_object
            except: pass

    # Some more shit
    try:
        attrs['bedrooms'] = int(attrs['bedrooms'])
    except:
        pass
    try:
        attrs['bathrooms'] = int(attrs['bathrooms'])
    except:
        pass
    try:
        attrs['other'] = attrs['other'].replace('\n', ', ')
    except:
        pass

    # Make english
    transaction_replace = {'Ενοικίαση': 'Rent', 'Πώληση': 'Sale'}
    orient_replace = {'Διαμπερές': 'Duplex', 'Γωνιακό': 'Corner', 'Προσόψεως': 'Facade'}
    type_replace = {'Γκαρσονιέρες': 'Studio', 'Μονοκατοικίες - Αυτόνομα κτίρια': 'Condo', 
                   'Μεγάλα Διαμερίσματα': 'Bigger Appartment', 'Δυάρια': 'Two Room', 'Τριάρια': 'Three Room', 'Εξοχικές Κατοικίες': 'Cottage'}
    type_of_type_replace = {'Οροφοδιαμέρισμα': 'Condo', 'Μεζονέτα': 'Maisonette', 'Δίχωρη': 'Two Room', 
                           'Μονόχωρη': 'One Room', 'Κτίριο': 'Building', 'Βίλλα': 'Villa', 
                            'Ρετιρέ': 'Penthouse', 'Δώμα': 'Penthouse'}
    heating_replace = {'Κεντρική Θέρμανση': 'Central', 'Αυτόνομη Θέρμανση': 'Independent'}
    view_replace = {'Απεριόριστη θέα': 'Unrestricted', 'Θέα θάλασσα': 'Sea', 'Θέα βουνό': 'Mountain', 'Θέα δάσος': 'Forest'}
    condition_replace = {'Άριστη Κατάσταση': 'Excellent', 'Ανακαινισμένο': 'Renovated', 'Καλή Κατάσταση': 'Good', 
                         'Νεόδμητο': 'Newly Built', 'Νεοδόμητο': 'Newly Built', 'Χρήζει Ανακαίνισης': 'Needs Renovation', 
                         'Ημιτελές': 'Unfinished', 'Υπό Κατασκευή': 'Under Construction'}

    columns = {'transaction': transaction_replace, 'orientation': orient_replace, 
               'type': type_replace, 'type_of_type': type_of_type_replace, 
               'heating': heating_replace, 'view': view_replace, 'condition': condition_replace}

    for search, replace in columns.items():
        for key, value in replace.items():
            try:
                attrs[search] = attrs[search].replace(key, value)
            except: pass

    return attrs

def Handle_bad_data(entry, urls):
    # Write to bad_data
    with open('bad_data.txt', 'a') as bad:
        bad.write(f'{entry}\n')

    # And remove from urls
    urls.remove(entry)
    return urls

def safety_copy():
    # Make a safety copy of data.csv
    try:
        df = pd.read_csv('data/data.csv')
    except:
        return
    df.to_csv('data/data_backup.csv')

def log(message):
    # Print to log.txt
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')
    with open('log.txt', 'a') as log:
        log.write(f'{timestamp} : {message}\n')

def write_to_disk(urls):
    # Write urls to utls.txt

    with open('urls.txt', 'a') as f:
        for item in urls:
            f.write(f'{item}\n')

def scrape(urls):         
    # main scraping and storing method

    count = 0
    try:
        df = pd.read_csv('data/data.csv')
    except:
        df = pd.DataFrame()

    for i, url in zip(tqdm(range(len(urls)), desc='Scraping'), urls):
        ad = get_response(page=None, url=url)
        if ad == False:
            urls = Handle_bad_data(url, urls)
            continue

        try:
            soup = BeautifulSoup(ad, 'html.parser')
        except Exception as e:
            print(e)
            urls = Handle_bad_data(url, urls)
            continue

        attrs = parse(soup)
        attrs = preprocess(attrs)
        if attrs == False:
            continue

        try:
            sr = pd.Series(attrs)
            df2 = pd.DataFrame(sr)
            df2 = df2.T
            df = pd.concat([df, df2])

            count += 1
        except Exception as e: 
            print(e)
            continue

    df = df.drop_duplicates(subset='code')
    df.to_csv('data/data.csv', index=False)
    print(f"Scraped {count} entities.")
    log(f"Scraped {count} entities.")
    write_to_disk(urls)

if __name__=='__main__':
    data_path = f'{os.getcwd()}/data/'
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    new_urls = get_urls()
    safety_copy()
    scrape(new_urls)
