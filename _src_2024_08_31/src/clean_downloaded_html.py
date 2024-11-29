import os
from src.file_functions import move_file, html_table_to_arrests, move_folder, file_size, html_table_to_dict, html_table_to_arrests
import pandas as pd
from bs4 import BeautifulSoup

Y = "\033[1;38;5;157m" #Bold Yellow
u = "\033[4m" #Underline
y = "\033[0;38;5;157m" #Yellow
B = "\033[1;4;38;5;33m" #Bold Blue
b = "\033[0;38;5;33m" #Blue
G = "\033[1;4;38;5;46m" #Bold Green
g = "\033[0;38;5;46m" #Green
R = "\033[1;4;38;5;196m" #Bold Red
r = "\033[0;38;5;196m" #Red
S = "\033[0m" #Reset

# if folder contains "folder_arrests.csv" and "folder_previous_arrests.csv" then it has already been processed, move it to "/_All" and skip
# if folder contains "incomplete_links.txt" then it has already been processed, move it to "/_All" and skip
# if folder contains no HTML files, scrape all the links from txt files and save to "all_links.txt", move to "/_All" and skip
# if folder contains HTML files, process them and move to "/_All"
# File Moving Functions

def move_file(file, old_folder, new_folder):
    old_name = os.path.join(old_folder, file)
    new_name = os.path.join(new_folder, file)
    new_dir = os.path.dirname(new_name)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    os.rename(old_name, new_name)
    

folder_list = os.listdir('_All')

keep_folders = []
for folder in folder_list:
    if not os.path.isdir(os.path.join('_All', folder)):
        continue
    if folder.startswith('_'):
        continue
    if folder.endswith('.7z'):
        continue
    if folder.startswith('src'):
        continue
    files = [f for f in os.listdir(os.path.join('_All', folder))]
    if f'_All//{folder}//{folder}_arrests.csv' in files:
        continue
    if len([f for f in files if f.endswith('.html')]) == 0:
        continue
    keep_folders.append(f'{os.path.join('_All', folder)}')
print(f"{G}{len(keep_folders)}{g} folders to process")

for folder in folder_list:
    text_files = [f for f in os.listdir(os.path.join(folder)) if ".txt" in f]
    
    all_links = []
    if len(text_files) == 0:
        continue
    if len(text_files) == 1 and 'all_links.txt' in text_files:
        continue
    if not 'incomplete_links.txt' in text_files:
        os.mkdir(os.path.join(folder, 'text_files'))
        
        for text_file in text_files:
            with open(os.path.join(folder, text_file), 'r') as f:
                all_links += f.readlines()
            move_file(text_file, folder, os.path.join(folder, 'text_files'))
        all_links = list(set([link.strip() for link in all_links]))
        with open('all_links.txt', 'w') as f:
            f.write('\n'.join(all_links))
    else:
        pass





# Start by moving all completed folders to _All
for f, folder in enumerate(os.listdir()):
    if not os.path.isdir(folder):
        continue
    elif 'incomplete_links.txt' in os.listdir(folder):
        move_folder(folder, '_All')
        print(f'{folder} already processed, moving to _All/{folder}')
        continue
    elif f'{folder}_arrests.csv' in os.listdir(folder):
        move_folder(folder, '_All')
        print(f'{folder} already processed, moving to _All/{folder}')
        continue

# Identify folders with no HTML files
    




from src.html_utils import extract_arrests, extract_all_links, extract_incomplete_links

def main():
    folder_list=['_All\\Kern County Sheriff', '_All\\Kings County Sheriff', '_All\\Monterey County Sheriff', '_All\\Napa County Sheriff', '_All\\Nevada County Sheriff', '_All\\Norwalk Sheriff Substation', '_All\\Oakland CHP', '_All\\Oakland Police', '_All\\Orange County Sheriff', '_All\\Palmdale Sheriff Substation', '_All\\Pico Rivera Sheriff Substation', '_All\\Placer County Sheriff', '_All\\Plumas County Sheriff', '_All\\Riverside County - Blythe Jail - Sheriff', '_All\\Riverside County - Robert Presley DC - Sheriff', '_All\\Riverside County - Southwest DC - Sheriff', '_All\\Riverside SD - Banning Smith Correctional Facility Sheriff', '_All\\Riverside SD - John Benoit Detention Center Sheriff', '_All\\Sacramento County Sheriff', '_All\\San Bernardino CHP', '_All\\San Bernardino County Sheriff', '_All\\San Diego CHP', '_All\\San Diego County Sheriff', '_All\\San Diego Police', '_All\\San Francisco CHP', '_All\\San Francisco County Sheriff', '_All\\San Francisco Police', '_All\\San Jose Police', '_All\\San Mateo County Sheriff', '_All\\San Mateo Police', '_All\\Santa Ana Police', '_All\\Santa Barbara County Sheriff', '_All\\Santa Clara County Sheriff', '_All\\Santa Clara Police', '_All\\Santa Cruz County Sheriff', '_All\\SantaClaraCounty', '_All\\Shasta County Sheriff', '_All\\Tuolumne County Sheriff']
    for f, folder in enumerate(folder_list):
        os.makedirs(f'{folder}//processed', exist_ok=True)
        print(f'{y}Processing {Y}{folder}{y}: ({Y}{f+1}{y} of {len(folder_list)}){S}')
        arrests_full, previous_arrests_full = extract_arrests(folder)
        all_links = extract_all_links(folder)
        incomplete_links = extract_incomplete_links(folder, arrests_full, all_links)


main()
