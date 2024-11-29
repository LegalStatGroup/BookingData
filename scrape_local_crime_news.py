import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import requests
import pandas as pd
from typing import Dict, List
from datetime import datetime

from env import cookies, headers
from src.utils import *
from src.local_news import local_news_main_content
from src.login import is_logged_in

agency_list_path = "agency_list.csv"

# 1. Fetch a list of agencies to scrape
def fetch_agency_list():
    response = requests.get('https://www.localcrimenews.com/welcome/agencylist', headers=headers, cookies=cookies)
    content = local_news_main_content(response.text, as_soup = True)

    table = content.find('table')
    return extract_links(table)

def make_all_agency_list(agency_list_path = None, update = True):
    new_agency_list = fetch_agency_list()
    new_agency_df = pd.DataFrame({
        'agency': [a for a in new_agency_list.keys()], 
        'agency_url': ['https://www.localcrimenews.com'+ a for a in new_agency_list.values()]
        })

    if agency_list_path:
        agency_df = pd.concat([pd.read_csv(agency_list_path), new_agency_df], ignore_index=True)
        agency_df = agency_df.drop_duplicates()
    
    if update == True:
        agency_df.to_csv(agency_list_path)
        return agency_df
    else:
        now = datetime.now().strftime('%Y_%m_%d')
        new_agency_df.to_csv(agency_list_path.replace('.csv', f'_{now}.csv'))
        return new_agency_df


# 2. Get this first page of each agency
def process_text(text, agency, url):
    return { 
        'agency': agency,
        'agency_url': url,
        'agency_response': local_news_main_content(text, as_soup=False)
            }

async def fetch_url(session: aiohttp.ClientSession, agency: str, url: str, headers: Dict, cookies: Dict) -> dict:
    """Fetch a single URL and return the response data in the desired format."""
    async with session.get('https://www.localcrimenews.com/' + url, headers=headers, cookies=cookies) as response:
        text = await response.text()
        if is_logged_in(text):
            return process_text(text)
        else:
            return Exception(f"Failed to fetch {url} -- not logged in")

async def fetch_all_agencies(all_agencies: Dict[str, str], headers: Dict, cookies: Dict) -> List[dict]:
    """Fetch all agency URLs concurrently and return formatted responses."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_url(session, agency, url, headers, cookies)
            for agency, url in all_agencies.items()
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any failed requests
        return [r for r in responses if not isinstance(r, Exception)]


def agency_search_results(first_page_response_text):
    agency_response_text = local_news_main_content(first_page_response_text, as_soup=True)
    agency_response_text = BeautifulSoup(first_page_response_text, 'html.parser')
    return agency_response_text.find_all('div', class_='col-sm-6 col-md-4')

def agency_page_count(first_page_response_text):    
    agency_response_text = local_news_main_content(first_page_response_text)
    total_pages = remove_html_tags(agency_response_text).split('Page 1 of ')[1].strip().replace(',', '')
    return int(total_pages)

agency_data = {}
for row in agency_df.iterrows():
    agency_data[row[0]] = {
        'agency': row[1]['agency'],
        'agency_url': row[1]['agency_url'],
        'pages': agency_page_count(row[1]['agency_response']),
        'results': agency_search_results(row[1]['agency_response'])
    }

# Run the async code
if __name__ == "__main__":
    all_agencies = get_agency_list(agency_list_path)
    first_page_responses = asyncio.run(fetch_all_agencies(all_agencies, headers, cookies))
    agency_df = pd.DataFrame(first_page_responses)
    agency_df[]
    
    agency_response_text = local_news_main_content(agency_df['agency_response'].iloc[0], as_soup=True)



for i, a in agency_data.items():
    agency=a['agency']
    url = a['agency_url']
    total_pages = a['total_pages']
    result_list = a['results'] #some results already exist
    for page in range(total_pages):
        response = requests.get(url+f'pg={page}', headers=headers, cookies=cookies, params=params)
        response_results = agency_search_results(response.text)
        agency_data[i]['results'].append(response_results)



import aiohttp
import asyncio
from typing import Dict, List
full_url = f"https://www.localcrimenews.com{url}pg={page}"

async def fetch_page(session: aiohttp.ClientSession, full_url: str, headers: Dict, cookies: Dict, params: Dict = None, data: Dict = None) -> str:
    """Fetch a single page and return its content."""
    async with session.get(full_url, headers=headers, cookies=cookies, params=params) as response:
        return await response.text()

async def process_agency(session: aiohttp.ClientSession, agency_id: str, agency_info: Dict, 
                        headers: Dict, cookies: Dict, params: Dict) -> Dict:
    """Process all pages for a single agency."""
    agency = agency_info['agency']
    url = agency_info['agency_url']
    total_pages = agency_info['total_pages']
    
    # Create tasks for all pages
    tasks = [
        fetch_page(session, url, page, headers, cookies, params)
        for page in range(total_pages)
    ]
    
    # Gather all responses
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process responses and filter out any errors
    results = []
    for response in responses:
        if not isinstance(response, Exception):
            results.extend(agency_search_results(response))
    
    # Combine with existing results
    agency_info['results'].extend(results)
    return {agency_id: agency_info}

async def process_all_agencies(agency_data: Dict) -> Dict:
    """Process all agencies concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            process_agency(session, agency_id, agency_info, headers, cookies, params)
            for agency_id, agency_info in agency_data.items()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Combine all results back into a single dictionary
        updated_agency_data = {}
        for result in results:
            updated_agency_data.update(result)
        
        return updated_agency_data

# Example usage
async def main():
    updated_data = await process_all_agencies(agency_data)
    return updated_data

# Run the async code
if __name__ == "__main__":
    updated_agency_data = asyncio.run(main())
