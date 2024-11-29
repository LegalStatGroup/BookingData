import asyncio
import json

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_cookies():
    return{
        'ci_session': 'ci_session=a%3A19%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%227d3f3a41dc8c7c10d2a19541871e8c2b%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A14%3A%2276.150.150.224%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A106%3A%22Mozilla%2F5.0+%28Windows+NT+10.0%3B+WOW64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F128.0.0.0+Safari%2F537.36%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1732821361%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A13%3A%22LAST_ACTIVITY%22%3Bi%3A1732821361%3Bs%3A6%3A%22UserId%22%3Bs%3A5%3A%2246886%22%3Bs%3A8%3A%22Username%22%3Bs%3A7%3A%22sela124%22%3Bs%3A9%3A%22FirstName%22%3Bs%3A4%3A%22Sela%22%3Bs%3A8%3A%22LastName%22%3Bs%3A7%3A%22Manning%22%3Bs%3A8%3A%22Address1%22%3Bs%3A0%3A%22%22%3Bs%3A4%3A%22City%22%3Bs%3A8%3A%22Berkeley%22%3Bs%3A5%3A%22State%22%3Bs%3A2%3A%22CA%22%3Bs%3A7%3A%22ZipCode%22%3Bs%3A5%3A%2294701%22%3Bs%3A11%3A%22PhoneNumber%22%3Bs%3A0%3A%22%22%3Bs%3A12%3A%22EmailAddress%22%3Bs%3A17%3A%22124sela%40gmail.com%22%3Bs%3A12%3A%22CustomerType%22%3Bs%3A6%3A%22Lawyer%22%3Bs%3A6%3A%22logged%22%3Bb%3A1%3Bs%3A12%3A%22is_logged_in%22%3Bb%3A1%3B%7D0c6d5b111aa6b276b99967ed456f57dd7a24a576',
        }

def get_headers():
    return {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'DNT': '1',
        'Origin': 'https://www.localcrimenews.com',
        'Referer': 'https://www.localcrimenews.com/welcome/myAccount',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="128", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

