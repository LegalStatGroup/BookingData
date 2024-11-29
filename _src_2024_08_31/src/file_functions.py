import os

import pandas as pd
from bs4 import BeautifulSoup


def move_file(file, folder):
    old_name = os.path.join(folder, file)
    new_name = os.path.join(folder, 'processed', file)
    new_dir = os.path.dirname(new_name)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    os.rename(old_name, new_name)

def move_folder(old_name, new_folder = '_All'):
    new_name = os.path.join('_All', old_name)
    os.rename(old_name, new_name)

def file_size(file):
    return os.path.getsize(file)    



def html_table_to_dict(table, uid):
    data = []
    for row in table.find_all('tr'):
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
        df = pd.DataFrame(data[1:], columns=data[0])
        df['uid'] = uid
    return df

def html_table_to_arrests(table, uid):
    data = {}
    tds = table.find_all('td')
    for i, td in enumerate(tds):
        if i % 2 == 1 and i < len(tds)-1:
            data[td.text] = str(tds[i+1].text).strip()
    df = pd.DataFrame(data, index=[0])
    df['uid'] = uid
    return df