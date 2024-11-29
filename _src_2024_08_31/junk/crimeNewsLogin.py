import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from junk.Login import LoginClient
from src.utils.error_functions import cprint, init_log, now
from src.utils.html_functions import (credentials, get_cookies, is_success,
                                      set_headers, test_connection)


def login(username, password, headers):
    load_dotenv(os.path.join(os.getcwd(), 'src', 'env', '.env'))
    username = os.getenv('CRIMENEWS_USERNAME')
    password = os.getenv('CRIMENEWS_PASSWORD')
    data = {'Username': username,'Password': password}
    headers = set_headers('chrome', 'https://www.localcrimenews.com/')
    response = requests.get('https://www.localcrimenews.com/', headers=headers)
    cookies = get_cookies(response)
    if response.status_code == 200:
        response2 = requests.post('https://www.localcrimenews.com/welcome/validateLogin', headers=headers, cookies=cookies, data=data)
        if response2.status_code == 200:
            cookies = get_cookies(response2)
            return get_cookies(response2)
    return None

def test_connection(test_url, headers, cookies, test_div = 'content grid'):
    """
    Test the connection to the website to see if the login was successful
    """
    headers = headers if headers else set_headers('chrome', 'https://www.localcrimenews.com/')
    test_url = 'https://www.localcrimenews.com/welcome/agencyarrests/23/Azusa_Police?pg=12'
    response = requests.get(test_url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser').find('div', class_=test_div)
    if response.status_code == 200 and soup:
        cprint('Logged In', 'green')  
        return True
    else:
        cprint('Login Failed', 'red')  
        return False

    