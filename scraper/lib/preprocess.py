import re
from datetime import datetime


class Preprocess():
    def __init__(self):
        self.transaction_replace = {
                        'Ενοικίαση': 'Rent', 
                        'Πώληση': 'Sale'
                        }
        self.orient_replace = {
                        'Διαμπερές': 'Duplex', 
                        'Γωνιακό': 'Corner', 
                        'Προσόψεως': 'Facade', 
                        'Εσωτερικό': 'Interior'
                        }
        self.type_replace = {
                        'Γκαρσονιέρες': 'Studio', 
                        'Μονοκατοικίες - Αυτόνομα κτίρια': 'Condo', 
                        'Μεγάλα Διαμερίσματα': 'Bigger Appartment', 
                        'Δυάρια': 'Two Room', 
                        'Τριάρια': 'Three Room', 
                        'Εξοχικές Κατοικίες': 'Cottage'
                       }
        self.type_of_type_replace = {
                        'Οροφοδιαμέρισμα': 'Condo', 
                        'Μεζονέτα': 'Maisonette', 
                        'Δίχωρη': 'Two Room', 
                        'Μονόχωρη': 'One Room', 
                        'Κτίριο': 'Building', 
                        'Βίλλα': 'Villa', 
                        'Ρετιρέ': 'Penthouse', 
                        'Δώμα': 'Penthouse'
                        }
        self.heating_replace = {
                        'Κεντρική Θέρμανση': 'Central', 
                        'Αυτόνομη Θέρμανση': 'Independent'
                        }
        self.view_replace = {
                        'Απεριόριστη θέα': 'Unrestricted', 
                        'Θέα θάλασσα': 'Sea', 
                        'Θέα βουνό': 'Mountain', 
                        'Θέα δάσος': 'Forest'
                        }
        self.condition_replace = {
                        'Άριστη Κατάσταση': 'Excellent', 
                        'Ανακαινισμένο': 'Renovated', 
                        'Καλή Κατάσταση': 'Good', 
                        'Νεόδμητο': 'Newly Built', 
                        'Νεοδόμητο': 'Newly Built', 
                        'Χρήζει Ανακαίνισης': 'Needs Renovation', 
                        'Ημιτελές': 'Unfinished', 
                        'Υπό Κατασκευή': 'Under Construction'
                        }
        self.energy_performance_index_replace = {
                        'Α': 'A', 'Α+': 'A+', 
                        'Β': 'B', 'B+': 'B+', 
                        'Γ': 'C', 'Γ+': 'C+',
                        'Δ': 'D', 'Δ+': 'D+', 
                        'Ε': 'E', 'E+': 'E+', 
                        'Z': 'F', 'Z+': 'F+', 
                        'H': 'G', 'H+': 'G+', 
                        'Θ': 'H', 'Θ+': 'H+',
                        'Εξαιρείται': 'Excluded', 
                        'Έκδοση σε εξέλιξη': 'In progress'
                        }
        self.stone_replace = {
                        'Διατηρητέο': 'Preserved',
                        'Πετρόκτιστο': 'Stone Built',
                        'Νεοκλασικό': 'Neoclassical',
                        'Προκατασκευή': 'Prefab',
                        'Λυόμενο': 'Prefab',
                        'Νεόκτιστο': 'Newly Built',
                        'Loft': 'Loft',
                        }


    def format_area(self, area):
        # Helper function 

        low = float(area.split('-')[0])
        high = float(area.split('-')[1])
        return (low+high)/2

    def preprocess(self, attrs):
        # Preprocess scraped data

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
                attrs['area'] = self.format_area(attrs['area'])
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
        not_accepted = ['Ζήτηση για Ενοικίαση', 'Ζήτηση για Αγορά', 'Ανταλλαγή']
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
            replace = {'Υπόγειο': -1, 'Ισόγειο': 0, 'Ημιώροφος': 0.5, 'Ημιυπόγειο': -0.5, 'Υπερυψωμένο': 0}
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
                 'Ιαν': 'Jan', 'Φεβ': 'Feb', 'Μαρ': 'Mar', 'Απρ': 'Apr', 'Μαη': 'May', 'Μάι': 'May', 'Μαϊ': 'May',
                 'Ιουν': 'Jun', 'Ιούν': 'Jun', 'Ιουλ': 'Jul', 'Ιούλ': 'Jul', 
                 'Αυγ': 'Aug', 'Αύγ': 'Aug', 'Σεπ':'Sep', 'Οκτ': 'Oct', 
                 'Νοε':'Nov', 'Νοέ': 'Nov', 'Δεκ': 'Dec'}

        today = datetime.today().strftime('%A %-d %b %Y')

        try:
            for key,value in dates.items():
                attrs['upload_date'] = attrs['upload_date'].str.replace(key, value)
            attrs['upload_date'] = attrs['upload_date'].str.replace(',', '')
            attrs['upload_date'] = attrs['upload_date'].str.replace('σήμερα', today)
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
        # Format coordinates

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
        columns = {'transaction': self.transaction_replace, 
                   'orientation': self.orient_replace, 
                   'type': self.type_replace, 
                   'type_of_type': self.type_of_type_replace, 
                   'heating': self.heating_replace, 
                   'view': self.view_replace, 
                   'condition': self.condition_replace,
                   'energy_performance_index': self.energy_performance_index_replace}

        for search, replace in columns.items():
            for key, value in replace.items():
                try:
                    attrs[search] = attrs[search].replace(key, value)
                except: pass

        return attrs
