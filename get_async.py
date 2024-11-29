# This is a class that encapsulates a set of urls (and their corresponding clean logic) to be fetched asynchronously 
# It can also be utilized as a template for other async scraping projects

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import requests
import pandas as pd
from typing import Dict, List
from datetime import datetime

from env import cookies, headers
from src.html_clean_utils import *
from src.local_news import local_news_main_content
from src.login import is_logged_in



# Function to process response text

# Function to know if response was successful

# Function to generate request parameters

class AsyncFetch:
    def __init__(self, session: aiohttp.ClientSession, fetch_data: str, headers: Dict, cookies: Dict = None, 
    params_function: Function = None, data_function: Function = None, is_success_function: Function = None, process_response_text_function: Function = None):
        self.session = session
        self.fetch_data = fetch_data
        self.headers = headers
        self.cookies = cookies
        self.url_function = url_function
        self.params_function = params_function
        self.data_function = data_function
        self.is_success_function = is_success_function
        self.process_response_text_function = process_response_text_function
    
    async def fetch(self):
        """Fetch a single page and return its content."""
        # Do I need to adjust anything for when cookies, data, or params are not used?


        async with self.session.get(url, headers, cookies, params, data) as response:
            # Check if the response was successful
            if self.is_success_function():
                response_text = await response.text()
                # If it was successful, process the response text
                return self.process_response_text_function(response_text)
            else:
                return Exception(f"Failed to fetch {self.full_url}")


    async def fetch_batch(self, batch_info: List):
        """Process all pages for a single agency."""
        # Create tasks for all pages
        tasks = [self.fetch(
            url = self.url_function(page_info),
            headers = self.headers,
            cookies = self.cookies,
            params = self.params_function(page_info),
            data = self.data_function(page_info),
            is_success_function = self.is_success_function,
            process_response_text_function = self.process_response_text_function
            ) for page_info in batch_info
        ]
        
        # Gather all responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses and filter out any errors
        results = []
        for response in responses:
            if not isinstance(response, Exception):
                results.extend(agency_search_results(response))
        
        return results



# Example usage
def url_function(batch_data, page):
    url = batch_data['agency_url']
    return f"https://www.localcrimenews.com{url}pg={page}"

def params_function():
    return None

def data_function():
    return None

from src.login import is_logged_in
def is_success_function(response_text):
    return is_logged_in(response_text)

from src.local_news import local_news_main_content
def agency_search_results(page_response_text):
    agency_response_text = local_news_main_content(page_response_text, as_soup=True)
    agency_response_text = BeautifulSoup(page_response_text, 'html.parser')
    return agency_response_text.find_all('div', class_='col-sm-6 col-md-4') # returns a list of divs

def process_response_text_function(response_text):
    return agency_search_results(response_text)


def main(agency_data):
    for i, a in agency_data.items():
        batch_info = [
            { 
                'agency': a['agency'], 
                'agency_url': a['agency_url'], 
                'page': page
                } for page in range(a['total_pages'])
            ]
        results = asyncio.run(fetch_batch(batch_info))
        agency_data[i]['results'].extend(results)



full_url = f"https://www.localcrimenews.com{url}pg={page}"

# Example usage
async def main():
    updated_data = await process_all_agencies(agency_data)
    return updated_data

# Run the async code
if __name__ == "__main__":
    updated_agency_data = asyncio.run(main())
        updated_agency_data = {}
        for result in results:
            updated_agency_data.update(result)
        
        return updated_agency_data
        # Combine with existing results
        agency_info['results'].extend(results)
        return {agency_id: agency_info}

# Function to process the response text
# Function to know if response was successfully fetched

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


