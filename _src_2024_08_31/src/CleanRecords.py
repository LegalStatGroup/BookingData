
import aiohttp
import asyncio
import json
import os
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.utils.crimeNewsLogin import login
from src.headers import get_headers
from src.utils.error_functions import global_colors
from src.utils.file_functions import list_files
from src.utils.html_functions import is_success, git_commit
colors = global_colors()
pd.set_option('display.max_columns', None)

headers = get_headers(browser='chrome', referer = 'https://www.localcrimenews.com/welcome/')



def two_column_table_to_dict(content, uid):
    table = content.find('table')
    df = pd.DataFrame({'UID': uid, 'Arrest Name': 'No Data Found'}, index=[0])
    if table:
        data = {'UID': uid, 'updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        df = pd.DataFrame([data])
        for row in table.find_all('tr'):
            if len(row.find_all('td')) == 2:
                cols = row.find_all('td')
                data[cols[0].text.strip()] = cols[1].text.strip()
        df = pd.DataFrame([data])
    return df

def grid_table_to_dict(content, uid):
    content = content.find('div', class_='sidebar-course-intro')
    soup = BeautifulSoup(str(content).replace("<br/>",","), 'html.parser')
    table = soup.find('table')
    df = pd.DataFrame({'UID': uid, 'Arrested_For': 'No Previous Arrests Found'}, index=[0])
    if table:
        data = []
        col_names = [col.text.strip().replace(':', '').replace(" ", "_") for col in table.find_all('th')] + ['Record_Link']

        for row in table.find_all('tr', class_='trLink'):  # Look for rows with 'trLink' class
            cols = [col.text.strip() for col in row.find_all('td') if col.text.strip()]
            onclick_content = row.get('onclick', '') # Extract the onclick attribute
            if "welcome/detail/" in onclick_content:
                ruid_link = onclick_content.split("welcome/detail/")[1].split(";")[0]
                cols.append(ruid_link)
            data.append(dict(zip(col_names, cols)))
        df = pd.DataFrame(data)
        df['UID'] = uid

    return df


file_list = list_files("data/records")
file_list = file_list + list_files("new_records")
len(file_list)

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





def get_completed_tasks(savepath):
    """
    savepath: list of paths to the files
    df_complete: DataFrame of the completed tasks
    Get the tasks that have already been completed
    """
    if len(savepath) == 1:
        files = [f for f in os.listdir(savepath[0]) if f.endswith('.html') and 'records_Async' in f]
    else:
        files = []
        for path in savepath:
            files2 = [f for f in os.listdir(path) if f.endswith('.html') and 'records_Async' in f]
            files = files + files2
    files = list(set(files))
    uids = [file.split('Async')[1].split('.')[0] for file in files]
    df_complete = pd.DataFrame({'uid': uids, 'filename': files})
    return df_complete

def get_tasks(files_to_scrape_path):
    """
    files_to_scrape_path: path
    df_full: DataFrame of the full tasks
    Get the full task list (from results scrape)
    """
    with open(files_to_scrape_path, 'r') as f:
        files_to_scrape = f.read().splitlines()
    webids = [file.split('/')[-2] for file in files_to_scrape]
    df_full = pd.DataFrame({'uid': webids, 'url': files_to_scrape})
    return df_full


def get_incomplete_tasks(files_to_scrape_path, savepath):
    df_complete = get_completed_tasks(savepath)
    df_full = get_tasks(files_to_scrape_path)
    df = pd.merge(df_full, df_complete, on='uid', how='outer', indicator=True)
    df['_merge'] = df['_merge'].astype(str).replace('left_only', 'to_scrape').replace('both', 'completed')
    print(df['_merge'].value_counts())
    df = df[df['_merge'] == 'to_scrape']

    tasks = df['url'].tolist()
    return tasks


async def fetch(session, url):
    print(f'Fetching {url}')
    async with session.get(url, headers = headers) as response:
        return await response.text()


async def scrape_content(tasks):
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(tasks):
            filename = url.split('/')[-2]
            html = await fetch(session, url)
            soup = BeautifulSoup(html, 'html.parser')
            if html:
                with open("new_records/records_Async" + filename + ".html", 'w', encoding='utf-8') as file:
                    file.write(str(soup))
                print(f"Scraped {i} of {len(tasks)}")
            if i % 1000 == 0 & i > 0:
                os.system('git add .')
                os.system('git commit -m "Scraped San Jose"')
                os.system('git push')

def main():
    savepath = "data/records"
    files_to_scrape_path = 'data/cities/SanJose/SanJose_links_to_scrape.txt'
    tasks = get_tasks(files_to_scrape_path, savepath)
    username = 'sela124'
    password = 'TrustNo1!'
    headers, cookies = login(username, password)
    if test_connection(1, headers, cookies):
        asyncio.run(scrape_content())



url = f'https://www.localcrimenews.com/welcome/newCities/san-jose-california-arrests.html?pg={page}'
test = BeautifulSoup(response.text, 'html.parser').find('div', class_='content') != None
test_connection(url, test, headers, cookies)
    