
import os
import json
import pandas as pd
import asyncio

def list_files(directory, ext = '.html'):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                file_list.append(os.path.join(root, file))
    return file_list

def data_len(data):
    if len(data) == 0:
        print(f"Error: No records found in response data")
        return data
    else:
        return len(data)

def data_type_match(data1, data2 = None, test_type = None):
    """
    data_type_match(data1, data2 = None, test_type = None)
    data1: data to compare
    data2: data to compare
    test_type: type to compare to
    # Example usage: 
    data_type_match(data, response_data, dict)
    """
    if data2:
        if test_type:
            return type(data1) == type(data2) == test_type
        else:
            return type(data1) == type(data2)
    elif test_type:
        return type(data1) == test_type

def load_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
        print(f"Loaded: {len(data)} records found in file: {file_name}")
    return data

def append_data(data, response_data):
    original_len = len(data)
    if data_type_match(data, response_data, dict):
        data.update(response_data)
    elif data_type_match(data, response_data, list):
        data.extend(response_data)
    elif data_type_match(data, response_data, pd.DataFrame):
        data._append(pd.DataFrame(response_data))
    else:
        data += response_data
    print(f"Appended: {len(response_data)} records to data (len({original_len} --> {len(data)})")
    return data

def save_json(data, file_name):
    with open(file_name, 'w') as f:
        json.dump(data, f)
    print(f"Saved: {len(data)} records to file: {file_name}")

def load_csv(file_name):
    data = pd.read_csv(file_name)
    print(f"Loaded: {len(data)} records found in file: {file_name}")
    return data

def save_csv(data, file_name):
    data.to_csv(file_name, index=False)
    print(f"Saved: {len(data)} records to file: {file_name}")

def load_list(file_name, split_on='\n'):
    with open(file_name, 'r') as f:
        data = f.read().split(split_on)
        print(f"Loaded: {len(data)} records found in file: {file_name}")
    return data

def save_list(data, file_name, join_with='\n'):
    if type(data[0]) == dict:
        with open(file_name, 'w') as f:
            json.dump(data, f)
    with open(file_name, 'w') as f:
        f.write(join_with.join(data))
    print(f"Saved: {len(data)} records to file: {file_name}")

def load_text(file_name):
    with open(file_name, 'r') as f:
        data = f.read()
        print(f"Loaded: {len(data)} characters found in file: {file_name}")
    return data

def save_text(data, file_name):
    with open(file_name, 'w') as f:
        f.write(data)
    print(f"Saved: {len(data)} characters to file: {file_name}")

def load_data(file_name):
    extension = file_name.split(".")[-1]
    if extension == 'json':
        if os.path.exists(file_name):
            return load_json(file_name)
        else:
            return {}
    elif extension == 'csv':
        if os.path.exists(file_name):
            return load_csv(file_name)
        else:
            return pd.DataFrame()
    elif extension == 'txt':
        if os.path.exists(file_name):
            return load_text(file_name)
        else:
            return ""

def save_data(data, file_name):
    if isinstance(data, dict):
        save_json(data, file_name)
    elif isinstance(data, list):
        save_list(data, file_name)
    elif isinstance(data, pd.DataFrame):
        save_csv(data, file_name)
    else:
        save_text(data, file_name)
    print(f"Saved: {len(data)} records to file: {file_name}")
    
def append_data(data, response_data):
    original_len = len(data)
    if len(response_data) == 0:
        print(f"Error: No records found in response data")
        return data
    
    if type(data) != type(response_data):
        print(f"Error: Data type mismatch")
        return data
    
    if isinstance(data, dict):
        data.extend(response_data)
    elif isinstance(data, list):
        data.append(data)
    elif isinstance(data, pd.DataFrame):
        data._append(pd.DataFrame(response_data))
    else:
        data += response_data
        print(f"Appended: {len(response_data)} records to data (len({original_len} --> {len(data)})")
    return data

def git_commit(message=None):
    os.system('git add .')
    os.system(f'git commit -m "{message}"')
    os.system('git push')
    print("Committed and pushed to git")



async def git_commit_async(message=None):
    proc = await asyncio.create_subprocess_shell('git add .')
    await proc.communicate()
    if message:
        proc = await asyncio.create_subprocess_shell(f'git commit -m "{message}"')
        await proc.communicate()
    proc = await asyncio.create_subprocess_shell('git push')
    await proc.communicate()
    print("Committed and pushed to git")


def pip_install(package):
    os.system(f'pip install {package}')