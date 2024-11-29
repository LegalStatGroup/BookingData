import asyncio
import json
from datetime import datetime
from typing import Dict, List

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup


async def fetch(session, url):
    print(f'Fetching {url}')
    async with session.get(url, headers = headers, cookies = cookies) as response:
        return await response.text()

async def scrape_agency_data(agency_data):
    async with aiohttp.ClientSession() as session:
        for agency in agency_data:
            html = await fetch(session, agency['url'])
            soup = BeautifulSoup(html, 'html.parser')
            
            if soup.find('div', class_='welcome-subheader') is None:
                agency['total_records'] = 0
            else:
                # Extract total records
                total_records_span = soup.find('div', class_='welcome-subheader').find_all('span', class_='records')[-1]
                agency['total_records'] = int(total_records_span.text.replace(',', ''))
            
            if soup.find('div', style="margin-top:5px; font-size:16px; font-weight:bold;") is None:
                agency['total_pages'] = 0

            else:
                # Extract total pages
                total_pages_span = soup.find('div', style="margin-top:5px; font-size:16px; font-weight:bold;").find_all('span', class_='records')[-1]
                agency['total_pages'] = int(total_pages_span.text.replace(',', ''))
            
        return agency_data

async def main():
    start_url = 'https://www.localcrimenews.com/welcome/agencylist'
    response = requests.get(start_url, headers = headers, cookies = cookies)
    links = BeautifulSoup(response.text, 'html.parser').find_all('a', class_='citylink')
    agency_links = [{'agency': link.text, 'url': f"https://www.localcrimenews.com{link['href']}"} for link in links if '/welcome/agencyarrests' in link['href']]
    data_dict = await scrape_agency_data(agency_links)
    
    # Save data_dict to JSON
    with open('agency_data.json', 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)

asyncio.run(main())

def get_agency_list(agency_list_path):
    with open(agency_list_path, 'r') as f:
        agency_list = json.load(f)
    sorted_agency_list = sorted(agency_list, key=lambda x: x['total_pages'], reverse=True)
    sorted_agency_list = [agency for agency in sorted_agency_list if agency['total_pages'] > 0]

    seen = set()
    sorted_deduped_agency_list = []

    for d in sorted_agency_list:
        # Convert dictionary to a tuple of its values, which can be hashed
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            sorted_deduped_agency_list.append(d)
    return sorted_deduped_agency_list