import requests
import json
from bs4 import BeautifulSoup
from env.headers import user_agent
from utils.html_operations import remove_html_tags, strip_whitespace, split_n_strip, split_to_dict
import pandas as pd
#from utils.file_operations import pip_install

dict_path = "data/cities/cities_to_scrape.json"

def load_json(file_path):
    with open('cities_to_scrape.json', 'r') as f:
        cities = json.load(f)
    return cities

cookies = {
    'ci_session': 'a^%^3A5^%^3A^%^7Bs^%^3A10^%^3A^%^22session_id^%^22^%^3Bs^%^3A32^%^3A^%^221f3845dd1000882376c8a52013dde783^%^22^%^3Bs^%^3A10^%^3A^%^22ip_address^%^22^%^3Bs^%^3A14^%^3A^%^22194.146.14.241^%^22^%^3Bs^%^3A10^%^3A^%^22user_agent^%^22^%^3Bs^%^3A111^%^3A^%^22Mozilla^%^2F5.0+^%^28Windows+NT+10.0^%^3B+Win64^%^3B+x64^%^29+AppleWebKit^%^2F537.36+^%^28KHTML^%^2C+like+Gecko^%^29+Chrome^%^2F121.0.0.0+Safari^%^2F537.36^%^22^%^3Bs^%^3A13^%^3A^%^22last_activity^%^22^%^3Bi^%^3A1708139287^%^3Bs^%^3A9^%^3A^%^22user_data^%^22^%^3Bs^%^3A0^%^3A^%^22^%^22^%^3B^%^7D120e85701dd5b8c89ea6f63238c95f84ed31d23b',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Origin': 'https://www.localcrimenews.com',
    'Referer': 'https://www.localcrimenews.com/welcome/citylist',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

#*********************** List of Cities ************************
response = requests.post('https://www.localcrimenews.com/index.php/welcome/getcities', headers=headers, cookies=cookies)
r = requests.get('https://www.localcrimenews.com/welcome/citylist', headers=headers, cookies=cookies)
soup = BeautifulSoup(r.text, 'html.parser')
tds = soup.find_all('td')
cities = {city.text.strip(): city.find('a', href=True)['href'] if city.find('a', href=True) else None for city in tds}
cities = {k: "https://www.localcrimenews.com/" + v for k, v in cities.items() if isinstance(v, str) and v.startswith('/welcome')}
with open('cities_to_scrape.json', 'w') as f:
    f.write(json.dumps(cities, indent=4))



#*********************** LDetermine Number of Records per City ************************
"""
# Fetch both city numbers and the first records so that county (found in record) can be easily determined
"""

def extract_results(response, cities, results):
    """
    Extract results from the response
    """
    soup = BeautifulSoup(response.text, 'html.parser').find_all('div', class_='col-md-4')
    results += [r for r in soup if r.find('h2')]
    print(len(results))

    pages = BeautifulSoup(response.text, 'html.parser').find_all('span', class_='records')
    pages = [p.text for p in pages if p]
    if pages:
        cities[city] = {
            'link': response.url,
            'total_records': pages[1],
            'total_pages': pages[3]
        }
    return cities, results


cities = load_json(dict_path)
results = []
for city, data in cities.items():
    if isinstance(data, str):
        print(data)
        response = requests.get(data, headers=headers, cookies=cookies)
        if response.status_code == 200:
            cities, results = extract_results(response, cities, results)
    elif isinstance(data, dict):
        pass
    else:
        print('Error: ', data)

city_result = "\n".join([str(r) for r in results])

# Save the individual records
with open('data/cities/city_result.text', 'w') as f:
    f.write(city_result)
    f.close()
    
# Save the city totals
with open('data/cities/cities_counts.json', 'w') as f:
    json.dump(cities, f)
    f.close()

df = pd.DataFrame(cities).T  
df['total_records'] = pd.to_numeric(df['total_records'].str.replace(',', ''), errors='coerce')
df['total_pages'] = pd.to_numeric(df['total_pages'].str.replace(',', ''), errors='coerce')
df.reset_index(inplace=True, drop=False).rename(columns={'index': 'city'}, inplace=True)
df.to_csv('data/cities/cities_counts.csv', index=False)


#*********************** Get Totals to Prioritize *****************************
# Get list of counties from results (did not do this during scrape because don't want to assume 1-to-1 relationship between city and county)
# List of counties by city
city_list = [
    BeautifulSoup(str(r), 'html.parser').find('span', class_='meta').get_text(strip=True).split(' – ', 1)[1].split(',', 1)[0] or "Unknown"
    for r in results
]

county_list = [
    BeautifulSoup(str(r), 'html.parser').find('div', class_='ft-item').get_text(strip=True).split('\nCounty:\n', 1)[1].split('\n', 1)[0] or "Unknown"
    for r in results
]

locations = pd.DataFrame({'city': city_list, 'county': county_list}).drop_duplicates()
locations.to_csv('data/cities/city_locations.csv', index=False)

# Merge with totals
merged_df = pd.merge(locations, df, on='city', how='outer', indicator=True)

"""
merged_df['_merge'].value_counts()
both          4312
right_only      71 <- there appear to be cities that exist that don't have their own city listing?!? Might be explained because it is city of arrest which might be different from cities reporting?
left_only       63
"""
# Merge on results and calculate county total records
merged_df = (merged_df[merged_df['_merge'] != 'right_only']
             .drop(columns='_merge').sort_values('total_records', ascending=False))

merged_df_group = (merged_df[['county', 'total_records']].groupby('county').sum()
                   .rename(columns={'total_records': 'total_county_records'}).reset_index())

# Merge on county totals
merged_df = (pd.merge(merged_df, merged_df_group, on='county', how='left')
             .sort_values(['total_county_records','total_records'], ascending=False))

merged_df.to_csv('data/cities/cities_counts.csv', index=False)






