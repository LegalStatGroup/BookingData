import requests

from utils.html_operations import get_cookies, is_success, credentials
from utils.assert_test import assert_test
from env.headers import set_headers



def dotenv_values(dotenv_path):
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path)
        return dict(os.environ)
    else:
        return {}
env = dotenv_values('.env')

def login(username, password):
    data = credentials(username, password)
    headers = set_headers()
    
    # Get Initial Cookies
    response = requests.get('https://www.localcrimenews.com/', headers=headers)
    if not is_success(response):
        return 
    cookies = get_cookies(response)

    # Login
    response = requests.post('https://www.localcrimenews.com/welcome/validateLogin', headers=headers, cookies=cookies, data=data)
    if not is_success(response):
        return
    auth_cookies = get_cookies(response)

    if assert_test('logged_in' in auth_cookies['ci_session']):
        print(colors.SUCCESS + "Login Successful" + colors.RESET)
        return headers, auth_cookies
    else:
        print(colors.ERROR + "Login Failed" + colors.RESET)
        return None, None
