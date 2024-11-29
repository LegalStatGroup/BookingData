import os
import asyncio
import json
from aiohttp import ClientSession, TCPConnector
from html_functions import set_headers
from src.crimeNewsLogin import login, test_connection
from error_functions import print_log, cprint, init_log, global_colors
from src.scrape_functions import print_soup
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from datetime import datetime
from time import sleep
import pandas as pd

#************************ Initialization ************************
load_dotenv(os.path.join(os.getcwd(), 'src', 'env', '.env'))
global_colors()
global cookies, headers
headers = set_headers(referer='https://www.localcrimenews.com/')


#************************ Custom Functions ************************
#Note: Replace with actual functions based on URL content

def now():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def two_column_table_to_dict(r, url):
    table = BeautifulSoup(r, 'html.parser').find_all('table')[1]
    data = {'UID': url.split("/")[-2], 'URL': url.split("/")[-1].split(".")[0], 'Arrest Name': 'No Data Found', 'updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if table:
        if 'Source' in table.text:
            for row in table.find_all('tr'):
                if len(row.find_all('td')) == 2:
                    cols = row.find_all('td')
                    data[cols[0].text.strip()] = cols[1].text.strip()
    return pd.DataFrame([data])


def grid_table_to_dict(r, url):
    df = pd.DataFrame({'UID': url.split("/")[-2], 'URL': url.split("/")[-1].split(".")[0], 'Arrested_For': 'No Previous Arrsts Founf Found', 'updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, index=[0])
    
    content = BeautifulSoup(r, 'html.parser').find('div', class_='sidebar-course-intro')
    if content:
        table = BeautifulSoup(str(content).replace("<br/>",","), 'html.parser').find('table')
        if table:
            data = []
            col_names = [col.text.strip().replace(':', '').replace(" ", "_") for col in table.find_all('th')] + ['UID', 'URL']
            for row in table.find_all('tr', class_='trLink'):  # Look for rows with 'trLink' class
                cols = [col.text.strip() for col in row.find_all('td') if col.text.strip()]
                onclick_content = row.get('onclick', '') # Extract the onclick attribute
                if "welcome/detail/" in onclick_content:
                    cols.append(onclick_content.split("/")[-2])
                    cols.append(onclick_content.split("/")[-1].split(".")[0])
                data.append(dict(zip(col_names, cols)))
            df = pd.DataFrame(data)
            df['UID'] = url.split("/")[-2]
            df['URL'] = url.split("/")[-1].split(".")[0]
            df['updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df

def save_content(full_df, df, agency, save_name):
    full_df = full_df._append(df, ignore_index=True)
    full_df.to_csv(os.path.join('ScrapeTEMPLATE', 'data', agency, f'{save_name}.csv'), index=False)
    return full_df


def create_tasks(url_list, chunk_size):
    chunked_tasks = [url_list[i:i+chunk_size] for i in range(0, len(url_list), chunk_size)]
    return chunked_tasks


#************************ Scrape ************************

async def fetch(session, url, headers, semaphore):
    async with semaphore:
        try:
            async with session.get(url, headers=headers) as response:
                return await response.text()
        except Exception as e:
            sleep(5)
            cprint(f"Error: {e} in {url} no response", 'red')
            try:
                async with session.get(url, headers=headers) as response:
                    return await response.text()
            except Exception as e:
                cprint(f"Error: {e} in {url} no response", 'red')
                return None
        

async def fetch_all_content(tasks, headers, limit=10):
    async with ClientSession(headers=headers) as session:
        semaphore = asyncio.Semaphore(limit)  # Limit the number of concurrent fetch operations
        fetch_tasks = [fetch(session, url, headers, semaphore) for url in tasks]
        return await asyncio.gather(*fetch_tasks)


#~~~~~~~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~

async def main(agency_dict, all_links, limit=30):
    """
    1. Iterate through the url_list in chunks of size chunk_size
    2. Fetch the content of each url in the chunk, limit the number of concurrent fetch operations
    3. Parse the content and save it to a file
    """
    all_current_arrests = pd.DataFrame()
    all_previous_arrests = pd.DataFrame()
    
    chunked_tasks = create_tasks(all_links, chunk_size=250)
    cprint(f"{a} of {len(all_links)} for {agency_dict['agency']} ({len(chunked_tasks)} chunks).", 'green')    

    for chunk, tasks in enumerate(chunked_tasks):
        if os.path.exists(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], f'previousArrests_{chunk}.csv')):
            cprint(f"Skipping chunk {chunk} of {len(chunked_tasks)}", 'blue')
            continue
        else:
            cprint(f"{agency_dict['agency']}:Starting chunk {chunk} of {len(chunked_tasks)}", 'yellow')
            responses = await fetch_all_content(tasks, headers, limit)
            current_arrests = [two_column_table_to_dict(r, url) for r, url in zip(responses, tasks) if r]
            all_current_arrests = save_content(all_current_arrests, current_arrests, agency_dict['agency'], save_name=f'currentArrests_{chunk}')
            previous_arrests = [grid_table_to_dict(r, url) for r, url in zip(responses, tasks) if r]
            all_previous_arrests = save_content(all_previous_arrests, previous_arrests, agency_dict['agency'], save_name=f'previousArrests_{chunk}')
    
    all_responses = {'current': all_current_arrests, 'previous': all_previous_arrests}
    return all_responses




url = chunked_tasks[43][0]
r = requests.get(url, headers=headers)
r = r.text
content = BeautifulSoup(r.content, 'html.parser')

#************************ Execution ************************
if __name__ == "__main__":
    with open('ScrapeTEMPLATE\\data\\agencies\\agencyResultCount_sorted.json', 'r') as f:
        agency_list = json.load(f)

    headers = set_headers(referer='https://www.localcrimenews.com/')
    


    for a, agency_dict in enumerate(agency_list):
        print(f"Agency {a+1} of {len(agency_list)}: {agency_dict['agency']}")
        with open(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], 'all_links.txt'), 'r') as f:
            all_links = f.read().split('\n')
        all_responses = asyncio.run(main(agency_dict, all_links, limit=20))

        all_responses['current'].to_csv(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], f'currentArrests_all.csv'), index=False)
        all_responses['previous'].to_csv(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], f'previousArrests_all.csv'), index=False)
        print(f"Saved {len(all_responses['current'])} current arrests and {len(all_responses['previous'])} previous arrests for {agency_dict['agency']}")



        #for file in file_list:
        #    os.remove(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], file))

        file_list = os.listdir(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency']))
        file_list = [file for file in file_list if file.startswith('searchResults_')]
        all_links = []
        for file in file_list:
            with open(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], file), 'r') as f:
                content = f.read()
                all_links.extend(content.split('\n'))
        all_links = [link for link in all_links if link]
        with open(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], 'all_links.txt'), 'w') as f:
            f.write('\n'.join(all_links))
