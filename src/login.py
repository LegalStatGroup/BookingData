import asyncio
import json

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.env import cookies, headers
from src.local_news import local_news_main_content
from src.utils import *

dotenv_path = '.env'

def is_logged_in(response_text):
    if 'Login to Local Crime News' in response_text:
        return False
    else:
        return True
        
def dotenv_values(dotenv_path):
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path)
        return dict(os.environ)
    else:
        return {}


def login_test(cookies, headers, username):
    login_test_response = requests.get('https://www.localcrimenews.com/welcome/myAccount', headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = local_news_main_content(login_test_response.text, as_soup=True)
        text = [strip_all(td.text) for td in soup.find_all('td')]
        if username in text:
            return True
    return False


def login(dotenv_path = '.env'):
    env = dotenv_values('.env')
    username = env['CRIMENEWS_USERNAME']
    password = env['CRIMENEWS_PASSWORD']
    

    response = requests.post('https://www.localcrimenews.com/welcome/validateLogin', headers=headers, cookies=cookies, data=data)
    if login_test(cookies, headers, username):
        cookies['ci_session'] = response.header['set_cookies']['ci_session'] if 'set_cookie' in response.headers.keys() else cookies['ci_session']
        return cookies, headers
    else:
        return None, None
    




