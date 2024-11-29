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


#************************ Initialization ************************
load_dotenv(os.path.join(os.getcwd(), 'src', 'env', '.env'))
global_colors()
global cookies, headers
headers = set_headers(referer='https://www.localcrimenews.com/')
cookies = login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
test_connection('https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers, cookies)

#************************ Custom Functions ************************
#Note: Replace with actual functions based on URL content

def now():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def current_response_to_file(response, filename = None):
    if not filename:
        filename = f"response_{now()}.txt"
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(str(response))
    return response

def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name

def save_content(contents, agency, chunk = now()):
    make_dir(os.path.join('ScrapeTEMPLATE', 'data', agency))

    with open(os.path.join('ScrapeTEMPLATE', 'data', agency, f'searchResults_{chunk}.txt'), 'w', encoding="utf-8") as f:
        f.write("\n".join([url for sublist in contents for url in sublist]) + '\n') # Flatten the list of lists into a single list of URLs
    return []

def parsing_function(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        links = soup.find('div', class_='content').find_all('a')
        hrefs = [link.get('href') for link in links]
        hrefs = [href for href in hrefs if href.startswith('https://www.localcrimenews.com/welcome/detail/')]
        return list(set(hrefs))
    except AttributeError as e:
        print_log(message=f"Error: {e} no content")
        current_response_to_file(html, filename=f"error_parsing.txt")
        return None

def create_tasks(agency_url, total_pages, chunk_size):
    tasks = []
    for i in range(1, total_pages + 1):
        if i == 1:
            tasks.append(agency_url)
        else:
            tasks.append(f"{agency_url}?pg={i}")

    chunked_tasks = [tasks[i:i+chunk_size] for i in range(0, len(tasks), chunk_size)]
    return chunked_tasks

def ping(url, headers, cookies):
    connected = test_connection(url, headers, cookies)
    i=0
    while connected:
        if connected:
            return cookies
        else:
            sleep(i*4)
            cookies = login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
            connected = test_connection(url, headers, cookies)
            i=i+1
            
            if i > 3:
                return False
    if not test_connection('https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers, cookies):
        cookies = login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
        test_connection('https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers, cookies)


#************************ Scrape ************************
async def fetch(session, url, headers, semaphore, max_retries=3):
    async with semaphore:
        for attempt in range(max_retries):
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        data.update({'url': str(response.url)})
                        return data
                    else:
                        print(f"Attempt {attempt + 1}: Failed to fetch {url} with status {response.status}")

            except Exception as e:
                cookies = ping('https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers, cookies)
                print(f"Attempt {attempt + 1}: Error {e} in {url}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff strategy
        print(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    

async def fetch(session, url, headers, cookies, semaphore):
    async with semaphore:
        try:
            async with session.get(url, headers=headers, cookies=cookies) as response:
                return await response.text()
        except Exception as e:
            try:
                cookies = login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
                test_connection('https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers, cookies)
                async with session.get(url, headers=headers, cookies=cookies) as response:
                    return await response.text()
            except Exception as e:
                print_log(message=f"Error: {e} in {url} no response")
                return None
        

async def fetch_all_content(tasks, headers, cookies, limit=10):
    async with ClientSession(headers=headers, cookies=cookies) as session:
        semaphore = asyncio.Semaphore(limit)  # Limit the number of concurrent fetch operations
        fetch_tasks = [fetch(session, url, headers, cookies, semaphore) for url in tasks]
        return await asyncio.gather(*fetch_tasks)


#~~~~~~~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~

async def main(agency_dict, cookies, chunk_size=250, limit=30):
    """
    1. Iterate through the url_list in chunks of size chunk_size
    2. Fetch the content of each url in the chunk, limit the number of concurrent fetch operations
    3. Parse the content and save it to a file
    """
    all_responses = []  # This will be a list of lists of URLs
    chunked_tasks = create_tasks(agency_dict['url'], agency_dict['total_pages'], chunk_size)
    
    max_chunks = len(chunked_tasks)
    chunked_tasks = chunked_tasks[max_chunks:max_chunks+1]
    for chunk, tasks in enumerate(chunked_tasks):
        if os.path.exists(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'], f'searchResults_{chunk}.txt')):
            continue
        else:
            cprint(f"{agency_dict['agency']}:Starting chunk {chunk} of {len(chunked_tasks)}", 'yellow')
            
            responses = await fetch_all_content(tasks, headers, cookies, limit)
            parsed_contents = [parsing_function(html) for html in responses if html]
            all_responses.extend(parsed_contents)
            all_responses = save_content(all_responses, agency_dict['agency'], chunk='max')

    
    #all_responses = save_content(all_responses, agency_dict['agency'], chunk='last')
    return all_responses







#************************ Execution ************************
if __name__ == "__main__":
    with open('ScrapeTEMPLATE\\data\\agencies\\agencyResultCount_sorted.json', 'r') as f:
        agency_list = json.load(f)

    headers = set_headers(referer='https://www.localcrimenews.com/')
    cookies = login(os.getenv('CRIMENEWS_USERNAME'), os.getenv('CRIMENEWS_PASSWORD'), headers)
    test_connection('https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12', headers, cookies)

    for a, agency_dict in enumerate(agency_list):
        if not os.path.exists(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency'])):
            os.mkdir(os.path.join('ScrapeTEMPLATE', 'data', agency_dict['agency']))
        
        cprint(f"{a} of {len(agency_list)} {agency_dict['agency']} ({agency_dict['total_pages']} pages).", 'green')    
        all_responses = asyncio.run(main(agency_dict, cookies, chunk_size=250, limit=20))
        save_content(all_responses, agency_dict['agency'], chunk='recent')        

#************************ End ************************
file_list = os.listdir('data/Alhambra Police')
file_list = [file for file in file_list if file.startswith('searchResults')]
links = []
for file in file_list:
    with open(os.path.join('data', 'Alhambra Police', file), 'r', encoding="utf-8") as f:
        content = f.read().split('\n')
    links += content
    print(len(links))
print(len(links))
links = list(set(links))
print(len(links))
save_content(links, 'Alhambra Police', chunk='Final')    
