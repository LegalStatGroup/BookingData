import requests
from bs4 import BeautifulSoup
import os
from src.html_functions import get_cookies, credentials, test_connection, is_success, set_headers
from src.error_functions import cprint, init_log, now
from dotenv import load_dotenv
from junk.Login import LoginClient



def login(username, password, headers):
    username = 'legalstat'
    password = 'vyxHzBB5Cffkppm'
    data = {'Username': username,'Password': password}
    headers = headers if headers else set_headers('chrome', 'https://www.localcrimenews.com/')
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

async def main():
    load_dotenv(os.path.join(os.getcwd(), 'src', 'env', '.env'))
    global headers, username, password, cookies
    headers = set_headers('chrome', 'https://www.localcrimenews.com/')
    username = os.getenv('CRIMENEWS_USERNAME')
    password = os.getenv('CRIMENEWS_PASSWORD')


    async with LoginClient(
        username = username, 
        password = password, 
        headers = headers, 
        base_url = 'https://www.localcrimenews.com/', 
        login_function = login(username, password, headers), 
        test_function = test_connection(), 
        ) as user:
        # Example fetch using the client
        cookies = user.login()
        #content = await user.async_fetch('/some-endpoint')
        #print(content)

#asyncio.run(main())
        
import requests

cookies = {
    'ci_session': 'a^%^3A19^%^3A^%^7Bs^%^3A10^%^3A^%^22session_id^%^22^%^3Bs^%^3A32^%^3A^%^22c0f8017500461cc6dcfe4bc335caf815^%^22^%^3Bs^%^3A10^%^3A^%^22ip_address^%^22^%^3Bs^%^3A14^%^3A^%^2276.150.150.224^%^22^%^3Bs^%^3A10^%^3A^%^22user_agent^%^22^%^3Bs^%^3A111^%^3A^%^22Mozilla^%^2F5.0+^%^28Windows+NT+10.0^%^3B+Win64^%^3B+x64^%^29+AppleWebKit^%^2F537.36+^%^28KHTML^%^2C+like+Gecko^%^29+Chrome^%^2F116.0.0.0+Safari^%^2F537.36^%^22^%^3Bs^%^3A13^%^3A^%^22last_activity^%^22^%^3Bi^%^3A1709714297^%^3Bs^%^3A9^%^3A^%^22user_data^%^22^%^3Bs^%^3A0^%^3A^%^22^%^22^%^3Bs^%^3A6^%^3A^%^22UserId^%^22^%^3Bs^%^3A5^%^3A^%^2246886^%^22^%^3Bs^%^3A8^%^3A^%^22Username^%^22^%^3Bs^%^3A7^%^3A^%^22sela124^%^22^%^3Bs^%^3A9^%^3A^%^22FirstName^%^22^%^3Bs^%^3A4^%^3A^%^22Sela^%^22^%^3Bs^%^3A8^%^3A^%^22LastName^%^22^%^3Bs^%^3A7^%^3A^%^22Manning^%^22^%^3Bs^%^3A8^%^3A^%^22Address1^%^22^%^3Bs^%^3A0^%^3A^%^22^%^22^%^3Bs^%^3A4^%^3A^%^22City^%^22^%^3Bs^%^3A8^%^3A^%^22Berkeley^%^22^%^3Bs^%^3A5^%^3A^%^22State^%^22^%^3Bs^%^3A2^%^3A^%^22CA^%^22^%^3Bs^%^3A7^%^3A^%^22ZipCode^%^22^%^3Bs^%^3A5^%^3A^%^2294701^%^22^%^3Bs^%^3A11^%^3A^%^22PhoneNumber^%^22^%^3Bs^%^3A0^%^3A^%^22^%^22^%^3Bs^%^3A12^%^3A^%^22EmailAddress^%^22^%^3Bs^%^3A17^%^3A^%^22124sela^%^40gmail.com^%^22^%^3Bs^%^3A12^%^3A^%^22CustomerType^%^22^%^3Bs^%^3A6^%^3A^%^22Lawyer^%^22^%^3Bs^%^3A6^%^3A^%^22logged^%^22^%^3Bb^%^3A1^%^3Bs^%^3A12^%^3A^%^22is_logged_in^%^22^%^3Bb^%^3A1^%^3Bs^%^3A13^%^3A^%^22LAST_ACTIVITY^%^22^%^3Bi^%^3A1709714297^%^3B^%^7Dc9fcbcc841835adb9d073e110aa1ff4f71fa1c45',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.6',
    'Connection': 'keep-alive',
    'Content-Length': '0',
    'DNT': '1',
    'Origin': 'https://www.localcrimenews.com',
    'Referer': 'https://www.localcrimenews.com/welcome/myAccount',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

response = requests.post('https://www.localcrimenews.com/index.php/welcome/getAgencies', headers=headers, cookies=cookies)
response.json()
with open('agencies.json', 'w') as f:
    json.dump(response.json(), f)