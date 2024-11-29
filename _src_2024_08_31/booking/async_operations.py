import aiohttp
import asyncio
import json
import os
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.crimeNewsLogin import login
from src.headers import get_headers
from src.error_functions import global_colors
from src.file_functions import list_files, load_data, save_data
from src.html_functions import is_success, git_commit_async, test_connection, get_cookies, credentials
colors = global_colors()
pd.set_option('display.max_columns', None)




file_list = list_files("data/records")
file_list = file_list + list_files("new_records")
len(file_list)

parameters = {
    'referer_url': 'https://www.localcrimenews.com/welcome/',
    'links_to_scrape_path': 'data/cities/SanJose/SanJose_links_to_scrape.txt',
    'save_path': "data/records"
    'save_ext': '.html'
}


#********************** Keep Task List Current ******************************
def list_completed_tasks(save_path, save_ext, return_df = False):
    """
    List all the files in the save_path with the save_ext extension
    """
    if return_df:
        return pd.DataFrame({'completed_files': list_files(save_path, ext = save_ext)})
    else:
        return list_files(save_path, ext = save_ext)


def list_all_tasks(links_to_scrape_path, return_df = False):
    """
    List all the tasks in the links_to_scrape_path
    """
    if return_df:
        return pd.DataFrame({'incomplete url': load_data(links_to_scrape_path)})
    else:
        return load_data(links_to_scrape_path)
    


def list_remaining_tasks(save_path, save_ext, links_to_scrape_path, return_df = False, merge_on = None):
    """
    List all the tasks that have not been completed
    """
    completed_tasks = list_completed_tasks(save_path, save_ext, return_df = return_df)
    all_tasks = list_all_tasks(links_to_scrape_path, return_df = return_df)

    if return_df:
        df = pd.merge(all_tasks, completed_tasks, on=merge_on, how='outer', indicator=True)
        df['_merge'] = df['_merge'].astype(str).replace('left_only', 'to_scrape').replace('both', 'completed')
        print(df['_merge'].value_counts())
        df = df[df['_merge'] == 'to_scrape']
        return df
    else:
        all_tasks_set = set(all_tasks)
        completed_tasks_set = set(completed_tasks)
        return list(all_tasks_set - completed_tasks_set)


#********************** Scrape Content ******************************
headers = get_headers(browser='chrome', referer = referer_url)

async def fetch(session, url):
    print(f'Fetching {url}')
    async with session.get(url, headers = headers) as response:
        return await response.text()

async def save_content(content, file_name, commit = True, commit_message = None):
    if content:
        save_data(content, file_name)

        if commit:
            await git_commit_async(commit_message)

def clean_content(html):
    pass

async def scrape_content(tasks, file_name, save_freq = 1000, commit = True, commit_message = None):
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(tasks):
            print(f"Scraped {i} of {len(tasks)}")
            html = await fetch(session, url)
            if is_success(html):
                content = clean_content(html)
            if i % save_freq == 0 and i > 0:
                save_content(content, file_name, commit = True, commit_message = None)
                



#********************** Clean Fetched Content ******************************


def main():
    savepath = "data/records"
    files_to_scrape_path = 'data/cities/SanJose/SanJose_links_to_scrape.txt'
    tasks = get_tasks(files_to_scrape_path, savepath)
    username = 'sela124'
    password = 'TrustNo1!'
    headers, cookies = login(username, password)
    if test_connection(1, headers, cookies):
        asyncio.run(scrape_content())






soup = BeautifulSoup(html, 'html.parser')



for i, file in enumerate(file_list):
    if i <= 306898:
        continue
    else:
        if i % 10000 == 0:
            arrests_full.to_csv(f'data/sanJose_fullArrests_{i}.csv', index=False)
            previous_arrests_full.to_csv(f'data/sanJose_previousArrests_{i}.csv', index=False)
            arrests_full = pd.DataFrame()
            previous_arrests_full = pd.DataFrame()

        with open(file, 'r', encoding='utf-8') as f:
            html = f.read()
        uid = file.split('_Async')[-1].split('.')[0]
        print(f'{i+1} of {len(file_list)}')

        content = BeautifulSoup(html, 'html.parser')
        arrests = two_column_table_to_dict(content, uid)
        if len(arrests)>0:

            arrests_full = pd.concat([arrests_full, arrests], ignore_index=True)
            previous_arrests = grid_table_to_dict(content, uid)
            previous_arrests_full = pd.concat([previous_arrests_full, previous_arrests], ignore_index=True)

for i, file in enumerate(file_list):
    string = ""
    if file.endswith(".html"):
        with open(file, 'r', encoding='utf-8') as f:
            html = f.read()
        if 'sidebar-course-intro' in html:
            string += html + "\n"
            print(f'{i+1} of {len(file_list)}')
        if i % 10000 == 0 and i > 0:
            with open(f'data/cities/SanJose/originalHTML_{i}.html', 'w', encoding='utf-8') as f:
                f.write(string)
            string = ""
    # delete the file after processing
        os.remove(file)



# Dict Version
    
    

def grid_table_to_dict(content, uid):
    content = content.find('div', class_='sidebar-course-intro')
    soup = BeautifulSoup(str(content).replace("<br/>",","), 'html.parser')
    table = soup.find('table')
    data = []
    full_record = [uid]  # Initialize with uid
    if table:
        col_names = [col.text.strip().replace(':', '').replace(" ", "_") for col in table.find_all('th')] + ['Record_Link']

        for row in table.find_all('tr', class_='trLink'):  # Look for rows with 'trLink' class
            cols = [col.text.strip() for col in row.find_all('td') if col.text.strip()]
            onclick_content = row.get('onclick', '') # Extract the onclick attribute
            if "welcome/detail/" in onclick_content:
                ruid_link = onclick_content.split("welcome/detail/")[1]
                ruid = ruid_link.split("/")[0].split("'")[0]
                full_record.append(ruid)  
                cols.append(ruid_link)
            data.append({ruid: dict(zip(col_names, cols))})
    else:
        data = [{'Arrested_For': 'No Previous Arrests Found'}]
    df = pd.DataFrame(data)
    df['uid'] = uid
    return df, full_record

with open('data/sanJose_fullArrests.json', 'w', encoding='utf-8') as f:
    json.dump(arrests_full, f, ensure_ascii=False, indent=4)

with open('data/sanJose_bookings.json', 'w', encoding='utf-8') as f:
    for arrest in arrests_full:
        f.write(json.dumps(arrest, ensure_ascii=False))
        f.write(',\n')
    arrests.to_json(f, orient='records', lines=True)
with open('data/sanJose_previousArrests.json', 'w', encoding='utf-8') as f:
    arrests_full.to_json(f, orient='records', lines=True)





#========================================











url = f'https://www.localcrimenews.com/welcome/newCities/san-jose-california-arrests.html?pg={page}'
test = BeautifulSoup(response.text, 'html.parser').find('div', class_='content') != None
test_connection(url, test, headers, cookies)
    