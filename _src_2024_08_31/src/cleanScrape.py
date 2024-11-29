import pandas as pd
import os
pd.set_option('display.max_columns', None)

def data_validation(col, pattern):
    if col.str.contains(pattern).sum() == 0:
        print(f'\033[1;4;38;5;196mError {col}: inconsistent data\033[0m')


rename_dict = {
    'image-heading':'name', 
    'meta': 'ageCity', 
    'ft-item': 'county', 
    'text-capitalize': 'charges',
    'text-capitalize href': 'link',
}




for county in ['fresno', 'sacramento', 'san_jose', 'santa cruz', 'san_bernardino', 'san_francisco']:
    print(county)
    files = [f for f in os.listdir("Webscrape\\raw") if county in f.lower() and f.endswith('.csv')]
    alldata = pd.DataFrame()

    for file in files:
        print(file)
        df = pd.read_csv("Webscrape\\raw\\" + file)

        df.rename(columns=rename_dict, inplace=True)
        # drop rows with all missing values
        df.dropna(how='all', inplace=True)
        print(df.columns)

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip().replace('  ', " ").replace('\n', ",")
                df[col] = df[col].fillna('')
        df['age'] = df['ageCity'].str.extract(r'(\d+)')
        df['city'] = df['ageCity'].str.split(' – ').str[1]

        charges = df['charges'].str.split(',')
        df['charges'] = charges

        df = df[['name', 'age', 'city', 'county', 'charges', 'link']]
        df['page'] = county
        alldata = pd.concat([alldata, df], ignore_index=True)
    alldata.to_csv(f'Webscrape\\clean\\{county}_results.csv', index=False)

