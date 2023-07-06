import pandas as pd

def set_dtypes(df):
    df['code'] = df['code'].astype('string')
    df['report_code'] = df['report_code'].astype('string')
    df['location'] = df['location'].astype('string')
    df['other'] = df['other'].astype('string')
    df['description'] = df['description'].astype('string')

    df['transaction'] = df['transaction'].astype('category')
    df['type'] = df['type'].astype('category')
    df['type_of_type'] = df['type_of_type'].astype('category')
    df['heating'] = df['heating'].astype('category')
    df['energy_performance_index'] = df['energy_performance_index'].astype('category')
    df['orientation'] = df['orientation'].astype('category')
    df['condition'] = df['conditon'].astype('category')
    df['name'] = df['name'].astype('category')
    df['view'] = df['view'].astype('category')
    df['stone'] = df['stone'].astype('category')

    df['floor'] = df['floor'].astype('int16')
    df['bathrooms'] = df['bathrooms'].astype('int16')
    df['bedrooms'] = df['bedrooms'].astype('int16')
    df['visits'] = df['visites'].astype('int16')
    df['wc'] = df['wc'].astype('int16')

    df['area'] = df['area'].astype('float16')
    df['price'] = df['price'].astype('float16')
    df['price_per_sqm'] = df['price_per_sqm'].astype('float16')

    df['negotiable'] = df['negotiable'].astype('bool')

    df['available_date'] = df['available_date'].astype('time')
    df['construction_year'] = df['available_date'].astype('time')
    df['renovation_year'] = df['renovation_year'].astype('time')
    df['upload_date'] = df['upload_date'].astype('time')

    return df

df = pd.read_csv('data/data.csv')
df = set_dtypes(df)
df.to_csv('data/data.csv', index=False)

