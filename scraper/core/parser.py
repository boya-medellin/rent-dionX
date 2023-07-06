from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):       # sanitization
    # Helper class to strip html tags from strings
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


class Parser():
    def __init__(self):
        self.labels = { 
                    'Κωδ. Αγγελίας': 'code', 
                    'Κωδ. Αναφοράς': 'report_code', 
                    'Τύπος': 'transaction', 
                    'Κατηγορία': 'type', 
                    'Περιοχή': 'location',
                    'Εμβαδόν': 'area', 
                    'Εμβαδό (τ.μ.):': 'area', 
                    'Τιμή': 'price', 
                    'Τιμή / τ.μ': 'price_per_sqm', 'Τύπος Ακινήτου:': 'stone',
                    'Είδος γκαρσονιέρας:': 'type_of_type', 
                    'Είδος Κατοικίας:': 'type_of_type',
                    'Είδος Μονοκατοικίας:': 'type_of_type', 
                    'Όροφος:': 'floor', 
                    'Υπνοδωμάτια:': 'bedrooms', 
                    'Μπάνια:': 'bathrooms', 
                    'WC:': 'wc', 
                    'Τύπος Θέρμανσης:': 'heating', 
                    'Δείκτης ενεργειακής απόδοσης:': 'energy_performance_index',
                    'Προσανατολισμός:': 'orientation', 
                     'Θέα:': 'view', 
                    'Άλλα Χαρακτηριστικά:': 'other',
                    'Ανανεώθηκε:': 'upload_date', 
                    'Διαθέσιμο από:': 'available_date', 
                    'Δημοσιεύτηκε:': 'upload_date', 
                    'Επισκέψεις:': 'visits',
                    'Κατάσταση:': 'condition', 
                    'Έτος κατασκευής:': 'construction_year',
                    'Έτος ανακαίνισης:': 'renovation_year'}

    def parse(self, soup):        
        # Data formatting method

        tags1 = list(soup.find_all('td', class_='title value'.split()))
        tags2 = soup.find_all('dl', class_='attribute')
        tags2 = [tag.find_all('dt dd'.split()) for tag in tags2]
        tags2 = [tag for tup in tags2 for tag in tup]                           # flatten list

        tags = tags1 + tags2
        tags = [ strip_tags(str(string)).strip('(,.)€ \n') for string in tags]  # format strings
        tags_zipped = [ (tags[i], tags[i+1]) for i in range(0, len(tags),2)]    # convert to list of tuples

        attrs = dict(tags_zipped)

        for old_key, new_key in self.labels.items():
            try:
                attrs[str(new_key)] = attrs.pop(str(old_key))
            except:
                pass

        # some more attributes
        attrs['name'] = strip_tags(str(soup.find('h1')))

        try: 
            attrs['description'] = strip_tags(str(soup.find("div", class_="classi-text mrg-top-md").find_all("p")[1])).strip('  \n').strip('\n').strip('()')
        except: 
            pass

        try:
            attrs['coordinates'] = str( str(soup.find('a',class_='btn btn-secondary')['href']).strip('https://www.google.com/maps/place/').split(',') )
        except:
            pass

        return attrs
