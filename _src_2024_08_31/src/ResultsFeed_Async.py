import asyncio
import json
import os
from datetime import datetime
from time import sleep

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

Y = "\033[0m\033[1;38;5;157m" #Bold Yellow
u = "\033[0m\033[4m" #Underline
y = "\033[0m\033[0;38;5;157m" #Yellow
B = "\033[0m\033[1;4;38;5;33m" #Bold Blue
b = "\033[0m\033[0;38;5;33m" #Blue
G = "\033[0m\033[1;4;38;5;46m" #Bold Green
g = "\033[0m\033[0;38;5;46m" #Green
R = "\033[0m\033[1;4;38;5;196m" #Bold Red
r = "\033[0m\033[0;38;5;196m" #Red
d = "\033[0m\033[0;38;5;240m" #dim
S = "\033[0m" #Reset

#1 ************************ Utility Functions *********************

def now():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name


def get_root_dir(filepath):
    return os.path.dirname(os.path.dirname(filepath))


def unlist_nested_list(nested_list, join_str = None):
    if join_str:
        return join_str.join([item for sublist in nested_list for item in sublist]) + join_str
    else:
        return [item for sublist in nested_list for item in sublist]


def unlist_list(lst, join_str = None):
    if join_str:
        return join_str.join(lst) + join_str
    else:
        return lst


def unlist(object, join_str):
    if isinstance(object, list):
        if isinstance(object[0], list):
            return unlist_nested_list(object, join_str)
        else:
            return unlist_list(object, join_str)
    else:
        return object
    
    
def write_text_list(content, filepath = None, append=False, overwrite=False):
    if os.path.exists(get_root_dir(filepath)):
        make_dir(get_root_dir(filepath))
    
    content_str = unlist(content, '\n')
    
    write_mode = 'a' if append and os.path.exists(filepath) else 'w'
    filepath = f"{filepath}_{now()}.txt" if write_mode == 'w' and os.path.exists(filepath) and not overwrite else filepath
    
    with open(filepath, write_mode, encoding="utf-8") as f:
        f.write(str(content_str))
    return content_str


def move_folder(folder, new_folder):
    new_dir = os.path.join(os.getcwd(), new_folder)
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    os.rename(folder, os.path.join(new_dir, folder))
    return os.path.join(new_dir, folder)

#2 ************************ HTML Functions ************************

def is_success(response):
    try:
        return response.status_code == 200
    except:
        return response.status == 200


def get_cookies(response):
    if not response.cookies:
        cprint("No cookies found", 'yellow')
        return None
    if not response.status_code == 200:
        cprint(f"Error: Status code {response.status_code}", 'red')
        return None
    cookies = {}
    for cookie in response.cookies:
        cookies[cookie.name] = cookie.value
    return cookies


def user_agent (browser='chrome'):
    if browser.lower() == 'firefox':
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    elif browser.lower() == 'edge':
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    elif browser.lower() == 'brave':
        return ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36','"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"')
    else:
        return ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"')


def set_headers(browser='chrome', referer = None):
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': referer if referer else 'https://www.google.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent (browser)[0],
        'sec-ch-ua': user_agent (browser)[1],
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }


#3 ************************ Log-In Functions ************************

def is_logged_in(response_text):
    if 'Login to Local Crime News' in response_text:
        return False
    else:
        return True


def login(username, password, headers):
    load_dotenv(os.path.join(os.getcwd(), 'src', 'env', '.env'))
    username = os.getenv('CRIMENEWS_USERNAME')
    password = os.getenv('CRIMENEWS_PASSWORD')
    data = {'Username': username,'Password': password}
    headers = set_headers('chrome', 'https://www.localcrimenews.com/')
    response = requests.get('https://www.localcrimenews.com/', headers=headers)
    cookies = get_cookies(response)
    if response.status_code == 200:
        response2 = requests.post('https://www.localcrimenews.com/welcome/validateLogin', headers=headers, cookies=cookies, data=data)
        if response2.status_code == 200:
            cookies = get_cookies(response2)
            return get_cookies(response2)
    return None


def test_connection(test_url = 'https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers = None, cookies = None):
    """
    Test the connection to the website to see if the login was successful
    Test URL must use a page  5.
    """
    headers = headers if headers else set_headers('chrome', 'https://www.localcrimenews.com/')
    cookies = cookies if cookies else login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
    response = requests.get(test_url, headers=headers, cookies=cookies)
    if is_success(response) and is_logged_in(response):
        print(f'{G}Logged In{S}')  
        return True
    else:
        print(f'{R}Login Failed{S}')  
        return False


def login_to_crime_news():
    headers = set_headers(referer='https://www.localcrimenews.com/')
    cookies = login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
    
    test_response = requests.get('https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers=headers, cookies=cookies)
    
    if is_success(response) and is_logged_in(response.text):
        return headers, cookies
    else:
        raise Exception("Login failed")
    
    
#4 ************************ Custom Functions ************************
def parse_content(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    cards = soup.find_all('div', class_='col-sm-6 col-md-4')
    cards_links = [card.find('a').get('href') for card in cards if card.find('a')]
    return cards_links


#5 ************************ Scrape Functions ************************

async def fetch(session, url, headers, cookies, semaphore):
    async with semaphore:
        async with session.get(url, headers=headers, cookies=cookies) as response:
            response_text = await response.text()
            if response_text:
                if is_logged_in(response_text):
                    return response_text
                else:
                    print(f"{r}Logged Out. Retrying...{S}")
                    headers, cookies = login_to_crime_news()
                    async with session.get(url, headers=headers, cookies=cookies) as retry_response:
                        retry_response_text = await retry_response.text()
                        if is_logged_in(retry_response_text):
                            return retry_response_text
                        else:
                            return None
            else:
                return None

        
async def fetch_all_content(urls, headers, cookies, limit=None):
    if not limit:
        limit = len(urls)
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        semaphore = asyncio.Semaphore(limit)  # Limit the number of concurrent fetch operations
        fetch_tasks = [fetch(session, url, headers, cookies, semaphore) for url in urls]
        gathered_responses = await asyncio.gather(*fetch_tasks)
        parsed_contents = [parse_content(response_text) for response_text in gathered_responses if response_text]
        return parsed_contents

#~~~~~~~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~

#************************ Initialization ************************
"""
1. Load environment variables
2. Set global colors
3. Set headers and login to get global cookies
4. Test connection
"""

# Login
load_dotenv(os.path.join(os.getcwd(), 'src', 'env', '.env'))
headers = set_headers(referer='https://www.localcrimenews.com/')
cookies = login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
test_connection(headers=headers, cookies=cookies)

# Get List of Agencies
with open('ScrapeTEMPLATE\\data\\agencies\\agencyResultCount_sorted.json', 'r') as f:
        agency_list = json.load(f)
agencies = [f for f in os.listdir('_missing') if '_' not in f and f != 'src']
agency_df = pd.read_csv('agency_list.csv').to_dict('records')
agency_list = [agency for agency in agency_df if agency['agency'] in agencies]   

#************************ Execution ************************


chunk_size = 250
connection_limit = 30
    

for a, agency_dict in enumerate(agency_list):
    if 'updated' in agency_dict.keys():
        continue
    # get number of pages
    agency_url = agency_dict['agency_url']
    response = requests.get(agency_url, headers=headers, cookies=cookies)
    records = BeautifulSoup(response.text, 'html.parser').find_all('span', class_='records')[1].text.replace(',', '') 
    agency_dict['total_pages'] = int(records) // 20 + 1
    print(f"{g}{a + 1} of {G}{len(agency_list)}{g}: {agency_dict['agency']} {G}({agency_dict['total_pages']}{g} total URLs).{S}")  
    
    # List all urls to fetch
    url_list = [agency_url] + [f"{agency_url}?pg={i}" for i in range(2, agency_dict['total_pages'] + 1)]
    url_chunks = [url_list[i:i+chunk_size] for i in range(0, len(url_list), chunk_size)]
    
    
    all_responses = []  # This will be a list of lists of URLs
    for chunk, tasks in enumerate(url_chunks):
        print(f"{B}{len(tasks)}{b} urls in {chunk + 1} (of {len(url_chunks)}){S}")
        parsed_responses = asyncio.run(fetch_all_content(tasks, headers, cookies, connection_limit))
        all_responses.extend(parsed_responses)

    all_responses = write_text_list(all_responses, os.path.join(agency_dict['agency'], "all_links.txt"), append=True, overwrite=False)
    agency_dict['updated'] = now()
    agency_list[a] = agency_dict
            
