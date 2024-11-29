
from bs4 import BeautifulSoup
from src.utils.error_functions import cprint


def init_error(current_count = 0):
    global error_count
    error_count = current_count 
    return error_count

def print_soup(soup, color = None):
    if color is None:
        from random import randint
        color = randint(100, 255)
    soup = BeautifulSoup(str(soup), 'html.parser')
    cprint(soup.prettify(), color)

    