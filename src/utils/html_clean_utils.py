import json
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


def remove_html_tags(text):
    return re.sub('<[^<]+?>', '', str(text))

def strip_all(string):
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string.replace('\n', '').replace('\t', '').replace('\r', '').strip()

def extract_all_links(soup, **kwargs):
    a_list = soup.find_all('a', **kwargs)
    return {strip_all(a.text): a['href'] for a in a_list}

def soup_to_string(soup):
    return str(soup.prettify())

def soup_to_json(soup):
    return json.loads(soup_to_string(soup))

def soup_to_soup(soup):
    return BeautifulSoup(soup_to_string(soup), 'html.parser')
