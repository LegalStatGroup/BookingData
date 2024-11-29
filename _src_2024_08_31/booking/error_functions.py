import os
from datetime import datetime
import inspect

"""
This module logs and prints.  Includes color and time functions.
global_colors(): returns a dictionary of color codes and saves select colors as global variables.
now(): returns the current date and time with optional string format.
timing(start_time, i): returns the time elapsed since start_time, with optional time per item.
cprint(message, color, end, sep): prints message in color, with optional end and sep.
current_context(): returns the name of the current file.
last_function_call(): returns the name of the last function called.
list_globals(): returns a dictionary of global variables.
init_log(log_path): initializes a log file and returns the path.
print_log(message, log_path, verbose, color): writes to log file and optionally prints message in color.
log_error(message, log_path, verbose): logs an error message, includes last function run and stored values, and prints it in red.
"""
def global_colors():
    global Y, u, y, B, b, G, g, R, r, d, S, colors
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
    colors = {
        'Y': Y,
        'u': u,
        'y': y,
        'B': B,
        'b': b,
        'G': G,
        'g': g,
        'R': R,
        'r': r,
        'S': S,
        'BoldYellow': Y,
        'Underline': u,
        'yellow': y,
        'BoldBlue': B,
        'blue': b,
        'BoldGreen': G,
        'green': g,
        'BoldRed': R,
        'red': r,
        'reset': S,
        'SUCCESS': G,
        'ERROR': R,
        'WARNING': Y,
        'INFO': b,
        'RESET': S,
    }
    return colors

def now(format = 'datetime', path = True):
    if format == 'date':
        now_string = datetime.now().strftime("%Y-%m-%d")
    elif format == 'time':
        now_string = datetime.now().strftime("%H:%M:%S")
    elif format == 'datetime':
        now_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif format == 'dt':
        now_string = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    else:
        now_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if path:
        now_string = now_string.replace(":", "_").replace("-", "_").replace(" ", "_")
    return now_string

def timing(start_time = None, i = None):
    if start_time:
        time_delta = now() - start_time
        if i:
            print(f"{Y}--- {i} pages scraped in {time_delta} (time per page:{time_delta / i}---{S}")
        else:
            print(f"{Y} --- Elapsed time: {time_delta} --- {S}")
    else:
        print(f"{Y} --- Start time: {now()} --- {S}")
    return now()

def cprint(message, color=None, end='\n', sep=' '):
        if color is None or color not in colors:
            color = 'reset'
        print(f"{colors[color]}{message}{colors['reset']}", end=end, sep=sep)

def current_context():
    return str(inspect.stack()[-1].filename).split('.')[0]

def last_function_call():
    caller_frame = inspect.currentframe().f_back
    code_obj = caller_frame.f_code
    function_name = code_obj.co_name
    return function_name

def list_globals():
    global_vars = {k: v for k, v in globals().items() if not k.startswith('__') and not callable(v)}
    return global_vars

def init_log(log_path=None, format='datetime'):
    now_string = now(format='datetime', path=True)
    if not log_path:
        log_path = f'log_{current_context()}_{now_string}.txt'
    else:
        if format == 'date':
            log_path = f'log_{log_path}_{now(format=True).split(" ")[0].replace("-", "_")}.txt'
        elif format == 'time':
            log_path = f'log_{now(format=True).split(" ")[-1].replace(":", "_")}.txt'
        elif format == 'datetime':
            log_path = f'log_{log_path}_{now(format=True)}.txt'
        elif format == 'dt':
            log_path = f'log_{log_path}_{now(format=True)}.txt'

    if not os.path.exists(log_path):
        with open(log_path, 'w') as f:
            f.write(f'Log file created: {now(format=True)}\n')
    return log_path

def print_log(message, log_path=None, verbose=True, color=None):
    if not log_path:
        files = os.listdir()
        files = [file for file in files if file.startswith('log_')]
        if files:
            log_path = files[0]
        else:
            log_path = init_log()
    # Determine message color based on its content, if not explicitly provided
    if color is None:
        if "Error" in message:
            color = R
        elif "Warning" in message:
            color = Y
        elif "Success" in message:
            color = G
        else:
            color = B
            
    if verbose:
        print(f"{color}{u}({now(format=True)}): {S}{color}{message} {S}")
        print(f"printed to log file: {log_path}")

    write_method = 'w' if not os.path.exists(log_path) else 'a'
    with open(log_path, write_method) as f:
        f.write(f'{now(format=True)}: {message}\n')

def log_error(message, log_path, verbose=True, ):
    if not message:
        message = "Error:"
    last_function = last_function_call()
    log_path = init_log()
    message = "\n ".join([message, f"Last Function: {last_function}", f"Stored Values: {list_globals()}"])
    print_log(message, log_path, verbose=True)

def assert_test(test, log = False):
    if test:
        if log:
            print_log(f"Test Passed: {last_function_call}", color='green')
        else:
            cprint("Test Passed", "green")
        return True

    else:
        if log:
            print_log(f"Test Failed: {last_function_call}", color='red')
        else:
            cprint("Test Failed", "red")
        return False


