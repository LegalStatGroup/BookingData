import asyncio
import json
import os
import re
from datetime import datetime

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.ResultsFeed_Async import set_headers
from src.html_utils import combine_text_files, extract_arrests, extract_previous_arrests

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



#1 ************************ Scrape Functions ************************

async def fetch(session, url, headers, semaphore):
    async with semaphore:
        async with session.get(url, headers=headers) as response:
            return await response.text()
        
async def fetch_all_content(urls, headers, limit=None):
    if not limit:
        limit = len(urls)
    async with aiohttp.ClientSession(headers=headers) as session:
        semaphore = asyncio.Semaphore(limit)  # Limit the number of concurrent fetch operations
        fetch_tasks = [fetch(session, url, headers, semaphore) for url in urls]
        gathered_responses = await asyncio.gather(*fetch_tasks)
        return gathered_responses


#************************ Execution ************************

def test_errors(urls):
    set_headers(referer = 'https://www.localcrimenews.com/')
    test_arrests = pd.DataFrame()
    test_previous_arrests = pd.DataFrame()
    
    for url in urls:
        print(url)
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print(f"{R}Error: in {url} \n {e} {S}")
            return response.text

        try:
            arrests = extract_arrests(response.text)
            test_arrests = pd.concat([test_arrests, arrests], ignore_index=True)
        except Exception as e:
            print(f"{R}Error: in parsing arrrests for{url} \n {e} {S}")
            return response.text
        
        try:
            previous_arrests = extract_previous_arrests(response.text)
            test_previous_arrests = pd.concat([test_previous_arrests, previous_arrests], ignore_index=True)
        except Exception as e:
            print(f"{R}Error: in parsing previous arrrests for{url} \n {e} {S}")
            return response.text

    return {'arrests': test_arrests, 'previous_arrests': test_previous_arrests}


if __name__ == '__main__':
    connection_limit = 10
    folders = [f for f in os.listdir() if os.path.isdir(f)]
    folders = [f for f in os.listdir() if os.path.isdir(f) and not f.startswith('_') and not f.startswith('.') and not f.startswith('src')]

        
        



def main(connection_limit = 10):
    headers = set_headers(referer = 'https://www.localcrimenews.com/')

for folder in folders:
    text_files = [f for f in os.listdir(os.path.join( folder, 'processed')) if ".txt" in f]
    all_links = []
    for text_file in text_files:
        with open(os.path.join(folder, 'processed', text_file), 'r', encoding='utf-8') as f:
            all_links += f.readlines()
    all_links = list(set([link.strip() for link in all_links if link.strip()]))
    
    url_chunks = [all_links[i:i+connection_limit] for i in range(0, len(all_links), connection_limit)]
    print(f"{y}{folder}: {len(all_links)} links ({len(url_chunks)} chunks) found{S}")
    
    arrests_full = pd.DataFrame()
    previous_arrests_full = pd.DataFrame()

    for chunk, tasks in enumerate(url_chunks):
        if chunk < 1425:
            continue
        print(f"{b}Chunk {chunk+1} of {len(url_chunks)}{S}")
        responses = asyncio.run(fetch_all_content(tasks, headers, connection_limit))
        arrests = [extract_arrests(page) for page in responses] 
        arrests_full = pd.concat([arrests_full] + arrests, ignore_index=True)
        previous_arrests = [extract_previous_arrests(page) for page in responses]
        previous_arrests_full = pd.concat([previous_arrests_full] + previous_arrests, ignore_index=True)
        
        if chunk % 1000 == 0 and chunk != 0:
            arrests_full.to_csv(f'{folder}//{folder}_arrests{chunk // 1000}.csv', index=False)
            previous_arrests_full.to_csv(f'{folder}//{folder}_previous_arrests{chunk // 1000}.csv', index=False)
            arrests_full = pd.DataFrame()
            previous_arrests_full = pd.DataFrame()       

        elif chunk == len(url_chunks) - 1:
            arrests_full.to_csv(f'{folder}//{folder}_arrests{chunk // 1000 + 1}.csv', index=False)
            previous_arrests_full.to_csv(f'{folder}//{folder}_previous_arrests{chunk // 1000 + 1}.csv', index=False)
    
    return {'arrests': arrests_full, 'previous_arrests': previous_arrests_full}




if __name__ == '__main__':
    folders = [f for f in os.listdir() if os.path.isdir(f) and not f.startswith('_') and not f.startswith('.') and not f.startswith('src')]
    for folder in folders:
        
        
        
        data = main(folder)
        data['arrests'].to_csv(f'{folder}//{folder}_arrests.csv', index=False)
        data['previous_arrests'].to_csv(f'{folder}//{folder}_previous_arrests.csv', index=False)
        
        
        
        


def fetch_arrests(headers, url_chunks, connection_limit = 10):
    arrests_full = pd.DataFrame()
    previous_arrests_full = pd.DataFrame()
    for chunk, tasks in enumerate(url_chunks):
        try:
            print(f"{b}Chunk {chunk+1} of {len(url_chunks)}{S}")
            responses = asyncio.run(fetch_all_content(tasks, headers, connection_limit))
            arrests = [extract_arrests(page) for page in responses] 
            previous_arrests = [extract_previous_arrests(page) for page in responses]
        except Exception as e:
            print(f"{R}Error: {e}{S}")
            return tasks
        
        arrests_full = pd.concat([arrests_full] + arrests, ignore_index=True)
        previous_arrests_full = pd.concat([previous_arrests_full] + previous_arrests, ignore_index=True)
        
    return {'arrests': arrests_full, 'previous_arrests': previous_arrests_full}

def fetch_all_arrests(headers, folders, connection_limit = 10):
    for folder in folders:
        # Get a list of links to fetch from previous search scrape
        all_links = combine_text_files(folder, move_to_processed=True, overwrite=True)
        url_chunks = [all_links[i:i+connection_limit] for i in range(0, len(all_links), connection_limit)]
        print(f"{y}{folder}: {len(all_links)} links ({len(url_chunks)} chunks) found{S}")
        
        try:
            # Fetch arrests
            headers = set_headers(referer = 'https://www.localcrimenews.com/')
            data = fetch_arrests(headers, url_chunks, connection_limit)

            arrests_full = data['arrests']
            previous_arrests_full = data['previous_arrests']
            
            arrests_full.to_csv(f'{folder}//{folder}_arrests.csv', index=False)
            previous_arrests_full.to_csv(f'{folder}//{folder}_previous_arrests.csv', index=False)
        except Exception as e:
            print(f"{R}Error: {e}{S}")
            return data


