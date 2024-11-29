import asyncio
import os

import aiohttp
import requests

from src.utils.error_functions import cprint, init_log, now
from src.utils.html_functions import set_headers

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

class LoginClient:
    """
    A class to represent a client that logs into a website and performs tests on the connection.
    """
    def __init__(self, username, password, headers, cookies, base_url, login_function, test_function):
        self.username = username or os.getenv('USERNAME')
        self.password = password or os.getenv('PASSWORD')
        self.base_url = base_url
        self.headers = headers or set_headers('chrome', base_url)
        self.login_function = login_function
        self.test_function = test_function

        self.session = None  # Initialized later in an async context
        self.cookies = cookies or self.login(username, password, headers)

    def __str__(self):
        return f'LoginClient: {self.username} (expires: {self.expires})'
    
    def __repr__(self):
        return f'LoginClient: {self.username} (expires: {self.expires})'
    
    async def __aenter__(self):
        self.session = await aiohttp.ClientSession().__aenter__()
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    def login(self, *args, **kwargs):
        self.cookies = self.login_function(*args, **kwargs)

    def ping(self, *args, **kwargs):
        return self.test_function(*args, **kwargs)
    
    def set_url(self, endpoint):
        if endpoint.startswith('http'):
            return endpoint
        elif endpoint.startswith('/'):
            return f'{self.base_url}{endpoint}'
        else:
            return f'{self.base_url}/{endpoint}'
        
    def fetch(self, endpoint, method='GET', **kwargs):
        fetch_url = self.set_url(endpoint)
        if method.upper() == 'GET':
            response = requests.get(fetch_url, headers=self.headers, cookies=self.cookies, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(fetch_url, headers=self.headers, cookies=self.cookies, **kwargs)
        else:
            raise ValueError("Unsupported HTTP method provided.")
        
        if response.status_code == 200:
            print(f"Fetch Successful: {response.status_code}")
            return response
        else:
            cprint(f"Fetch Error: {response.status_code}", color='red')
            return None

    def get(self, endpoint, **kwargs):
        return self.fetch(endpoint, method='GET', **kwargs)
    
    def post(self, endpoint, **kwargs):
        return self.fetch(endpoint, method='POST', **kwargs)
            
    async def async_fetch(self, endpoint, method='GET', verbose = False, **kwargs):
        if verbose:
            cprint(f"Fetching: {endpoint}", log_path=self.log_path, color='blue')
        fetch_url = self.set_url(endpoint)
        try:
            async with self.session.request(method, fetch_url, headers=self.headers, cookies=self.cookies, **kwargs) as response:
                return await response.text()
        except Exception as e:
            cprint(f"Error: {e} in {fetch_url}", log_path=self.log_path, color='red')
            return None

    
    async def async_fetch_all(self, endpoints, limit=10):
        """
        Fetch all content concurrently, respecting the limit on concurrent operations.
        """
        semaphore = asyncio.Semaphore(limit)
        tasks = [self.async_fetch(endpoint, semaphore) for endpoint in endpoints]
        return await asyncio.gather(*tasks)

    async def close(self):
        """
        Close the aiohttp session.
        """
        await self.session.close()


