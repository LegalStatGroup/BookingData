import asyncio
import json

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup

from env import cookies, headers
from src.utils import *



def local_news_main_content(response_text, as_soup=False):
    main_content = '\n'.join(response_text.split('<!-- END / SIDEBAR CATEGORIES -->')[1:]).split('<!-- FOOTER -->')[0].split('<!-- end .container -->')[0]
    if as_soup:
        return BeautifulSoup(main_content, 'html.parser')
    else:
        return main_content