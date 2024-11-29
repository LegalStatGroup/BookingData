import json
import re
import subprocess
import urllib.parse
from random import randint
from time import sleep

import requests
from dotenv import load_dotenv

from src.utils.error_functions import *

Y = "\033[1;38;5;157m" #Bold Yellow
u = "\033[4m" #Underline
y = "\033[0;38;5;157m" #Yellow
B = "\033[1;4;38;5;33m" #Bold Blue
b = "\033[0;38;5;33m" #Blue
G = "\033[1;4;38;5;46m" #Bold Green
g = "\033[0;38;5;46m" #Green
R = "\033[1;4;38;5;196m" #Bold Red
r = "\033[0;38;5;196m" #Red
d = "\033[0;38;5;240m" #dim
S = "\033[0m" #Reset
    
def decode_html(encoded_string):
    return urllib.parse.unquote(encoded_string)

def encode_html(decoded_string):
    return urllib.parse.quote(decoded_string)

def is_success(response):
    if response.status_code == 200:
        print(f"{G}Success{S}")
        return True
    else:
        print(f"{R}Failed{S}")
        return False

def text_in_html(response, text, context=200):
    for t in response.text.find_all(text):
        if text in t:
            start_position = t.index(text)
            end_position = start_position + len(text)
            begin = max(0, start_position - context)
            end = min(len(t), end_position + context)
            print(y + t[begin:start_position] + G + t[start_position:end_position] + y + t[end_position:end] + S)
    return response.text

def nap(min_time=1, max_time=3):
    print("...Z...Z...Z")
    sleep(randint(min_time, max_time))

def git_commit(file_name, message=None):
    if message == None:
        message = f"Updated file: {file_name}"
    subprocess.run(['git', 'add', file_name])
    subprocess.run(['git', 'commit', '-m', message])
    subprocess.run(['git', 'push'])

def pip_install(package):
    subprocess.run(['pip', 'install', package])

def pip_install_requirements(file_name):
    subprocess.run(['pip', 'install', '-r', file_name])
    
def save_data(data, file_name):
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
    else:
        with open(file_name, 'w') as f:
            f.write(data)
    print(f"Saved: {len(data)} records to file: {file_name}")
    git_commit(file_name, f"Updated data: {file_name}")

def remove_html_tags (text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def strip_whitespace (text):
    text = re.sub(r'\n+', ' ', text).strip()
    return re.sub(r'\s+', ' ', text).strip()

def split_n_strip (text, split_on):
    return [t.strip() for t in text.split(split_on) if t]

def split_to_dict(text, split_on=':'):
    text_dict = {}
    pairs = re.findall(r'([^:]+):([^:]+)', text)
    for pair in pairs:
        key = pair[0].strip()
        value = pair[1].strip()
        text_dict[key] = value
    return text_dict

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


def credentials(username = None, password = None):
    load_dotenv(os.path.join(os.getcwd(), 'src', 'env', '.env'))
    try:
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
    except:
        try:
            username = input("Enter Username: ")
            password = input("Enter Trustworthy Password: ")
        except:
            cprint("Error: No credentials provided", 'red')
    return  {'Username': username, 'Password': password}

def enter_login(username = None, password = None):
    return credentials(username, password)

def test_connection(url, headers, cookies):
    """
    Test the connection to the website to see if the login was successful
    """
    response = requests.get(url, headers=headers, cookies=cookies)
    if is_success(response):
        cprint("Connection Successful", 'green')
        return True
    else:
        cprint("Connection Failed", 'red')
        return False


def user_agent (browser='chrome'):
    if browser == 'firefox':
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    elif browser == 'edge':
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    elif browser == 'brave':
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

def get_headers(browser='chrome', referer = None):
    return set_headers(browser, referer)
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
