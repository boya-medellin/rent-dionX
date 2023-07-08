# Rent:
# 1. Which region has the highest median price?

# 2. Which region has the highest median area?
# 2.1 Relation between price and area

# 3. Which region has the highest relative price?
# 3.1 Relation between relative price and area.

# 4. Are rent prices that are non-negotiable cheaper?

# 5. Which region is the most sought-after?  -> visits
# 5.1 Relation between visits and price

# 6. Bins

# 7. Timeseries

# 8. Principal Component Analysis

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from prepare import PrepareData

# Supress Warnings
import warnings
def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter(action='ignore')
    fxn()
warnings.simplefilter("ignore", category=FutureWarning)


# Read data
df = pd.read_csv('../data/data.csv')


###################
#####  RENT  ######
###################

rent = df[df['transaction'] == 'Rent']

prepare = PrepareData(rent)
rent = prepare.prepare()
prepare.outliers.plot_outliers(include_all=True)


# 1. Which region has the highest mean price?

group_region_price = rent.groupby('name').price.describe().sort_values(by=['mean'], ascending=False)
group_region_price[group_region_price['count'] > 100].head()


# 2. Which region has the highest mean area?

group_region_area = rent.groupby('name').area.describe().sort_values(by=['mean'], ascending=False)
group_region_area[group_region_area['count'] > 100].head()


# 3. Which region has the highest relative price?
# Kinda reduntant but ok

mean_price = np.mean(rent.price)

rent_rel = rent
rent_rel['price'] = rent_rel['price'] - mean_price

group_region_price_rel = rent_rel.groupby('name').price.describe().sort_values(by=['mean'], ascending=False)
group_region_price_rel[group_region_price_rel['count'] > 100].head()


# 3.1 Relation between price and area

# Lets graph it out
plt.scatter(x=rent.price, y=rent.area)
plt.xlabel('Price')
plt.ylabel('Area')
plt.show()


# 4. Are rent prices that are non-negotiable cheaper?
# Kinda stupid but ok

group_neg_price = rent.groupby('negotiable').price.describe().sort_values(by=['mean'], ascending=False)

# Need a bar plot
bar_colors = ['tab:blue', 'tab:red']
plt.bar(x=['True', 'False'], height=[group_neg_price['mean'][0], group_neg_price['mean'][1]],
        color=bar_colors)
plt.show()


# 5. Which region is the most sought-after?  -> visits
group_region_visits = rent.groupby('name').visits.describe().sort_values(by=['mean'], ascending=False)
relative = ( group_region_visits['mean'] / group_region_visits['count'] ).sort_values(ascending=False)

# Bar plot it
plt.figure(figsize=(5,2))

plt.barh(y=relative.index[:], width=relative.values[:])
plt.yticks(fontsize=8)
plt.xlabel('Visits per Instance')
plt.show()


# 5.1 Relation between visits and price

# 6. Bins
bins = pd.IntervalIndex.from_tuples( 
            [(100,150), 
             (150,300), 
             (300,400), 
             (400,500), 
             (500, 1000), 
             (1000, 2000)])
binned_rent = pd.cut(rent.price, bins=bins)
group_binned = binned_rent.groupby(binned_rent.values)

intervals_dict = dict(zip(list(group_binned.describe().index), list(group_binned.describe()['count'])))
intervals_tupples = [ (inter.left, inter.right) for inter in list(intervals_dict.keys())]
intervals_dict_plain = dict(zip(intervals_tupples, list(intervals_dict.values())))
intervals_dict_text = dict(zip(intervals_tupples, list(intervals_dict.values())))
ranges = [str(ran) for ran in list(intervals_dict_plain)]

# plot it because it feels good
plt.barh(y=ranges, width=intervals_dict_plain.values(), color='orange')
plt.yticks(fontsize=16)
plt.xlabel('Rent Prices')
plt.show()




# MAP

import plotly.express as px

group_region_price = rent.groupby('name').price.describe().sort_values(by=['mean'], ascending=False)
# group_region_price[group_region_price['count'] > 100]

