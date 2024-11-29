import os

import pandas as pd
from bs4 import BeautifulSoup

Y = "\033[1;38;5;157m" #Bold Yellow
u = "\033[4m" #Underline
y = "\033[0;38;5;157m" #Yellow
B = "\033[1;4;38;5;33m" #Bold Blue
b = "\033[0;38;5;33m" #Blue
G = "\033[1;4;38;5;46m" #Bold Green
g = "\033[0;38;5;46m" #Green
R = "\033[1;4;38;5;196m" #Bold Red
r = "\033[0;38;5;196m" #Red
S = "\033[0m" #Reset

# if folder contains "folder_arrests.csv" and "folder_previous_arrests.csv" then it has already been processed, move it to "/_All" and skip
# if folder contains "incomplete_links.txt" then it has already been processed, move it to "/_All" and skip
# if folder contains no HTML files, scrape all the links from txt files and save to "all_links.txt", move to "/_All" and skip
# if folder contains HTML files, process them and move to "/_All"
# File Moving Functions

import asyncio
import json
import os
import re
from datetime import datetime

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup

from ResultsFeed_Async import get_headers

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

#1 ************************ List of Links Functions ************************

def move_file(file, old_folder, new_folder):
    old_name = os.path.join(old_folder, file)
    new_name = os.path.join(new_folder, file)
    new_dir = os.path.dirname(new_name)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    os.rename(old_name, new_name)

def move_to_processed(file, folder):
    old_name = os.path.join(folder, file)
    new_name = os.path.join(folder, 'processed', file)
    new_dir = os.path.dirname(new_name)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    os.rename(old_name, new_name)
    
    
def combine_text_files(folder, move=True, overwrite=False):
for folder in folders:
    os.makedirs(f'{folder}//processed', exist_ok=True)
    text_files = [f for f in os.listdir(folder) if ".txt" in f]
    all_links = []

    for text_file in text_files:
        with open(os.path.join(folder, text_file), 'r', encoding='utf-8') as f:
            all_links += f.readlines()
        os.rename(os.path.join(folder, text_file), os.path.join(folder, 'processed', text_file))
        
    all_links = list(set([link.strip() for link in all_links if link.strip()]))

    with open(folder + 'all_links.txt', 'w', encoding='utf-8') as f:
        f.writelines(all_links)


        return all_links
    
#2 ************************ Cleaning Functions ************************
def html_table_to_dict(table, uid):
    data = []
    for row in table.find_all('tr'):
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
        df = pd.DataFrame(data[1:], columns=data[0])
        df['uid'] = uid
    return df

def html_table_to_arrests(table, uid):
    data = {}
    tds = table.find_all('td')
    for i, td in enumerate(tds):
        if i % 2 == 1 and i < len(tds)-1:
            data[td.text] = str(tds[i+1].text).strip()
    df = pd.DataFrame(data, index=[0])
    df['uid'] = uid
    return df

def extract_arrests(page):
    if '<!-- END / SIDEBAR CATEGORIES -->' not in page:
        return None
    if 'California cities with reported arrests' in page.split('<title>')[1].split('</title>')[0]:
        return None
    uid = page.split('<title>')[1].split('</title>')[0].split(' - ')[1]
    page = page.split('<!-- END / SIDEBAR CATEGORIES -->')[1]
    soup = BeautifulSoup(page, 'html.parser')
    arrest = soup.find('table')
    df = pd.DataFrame({'uid': uid, 'Arrested_For': 'No Arrests Found'}, index=[0])
    if arrest:
        df = html_table_to_arrests(arrest, uid)
    return df
        
def extract_previous_arrests(page):
    if '<!-- END / INTRODUCTION -->' not in page:
        return None
    if 'California cities with reported arrests' in page.split('<title>')[1].split('</title>')[0]:
        return None
    uid = page.split('<title>')[1].split('</title>')[0].split(' - ')[1]
    page = page.split('<!-- END / INTRODUCTION -->')[1]
    soup = BeautifulSoup(page, 'html.parser')
    previous_arrest = soup.find('table')
    previous_arrest_df = pd.DataFrame({'uid': uid, 'Arrested_For:': 'No Previous Arrests Found'}, index=[0])
    if previous_arrest:
        previous_arrest_df = html_table_to_dict(previous_arrest, uid)
    return previous_arrest_df



#3 ************************ Checking Functions ************************

    


def extract_incomplete_links(folder, arrests_full, all_links):
    all_links = pd.DataFrame({'uid': [link.split('detail/')[1].split('/')[0] for link in all_links if 'detail/' in link]})
    completed_links = pd.DataFrame({'uid': arrests_full['uid'].unique()})
    incomplete_links = pd.merge(all_links, completed_links, on='uid', how='outer', indicator=True)
    print(f'{y}...Incomplete_links:{Y}{incomplete_links['_merge'].value_counts()}{S}')
    incomplete_links = incomplete_links[incomplete_links['_merge'] == 'right_only']['uid'].unique().tolist()
    with open(f'{folder}//incomplete_links.txt', 'w') as f:
        f.write('\n'.join(incomplete_links))
    return incomplete_links