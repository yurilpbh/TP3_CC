import traceback
import datetime
import json
import pandas as pd
import redis
import os
import importlib
import time
import sys

from icecream import ic 

REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', None)

def time_format():
    return f'{datetime.datetime.now()}|> '
    
ic.configureOutput(prefix=time_format)

def log(msg):
    ic(msg)

if not REDIS_OUTPUT_KEY:
    log("ENV `REDIS_OUTPUT_KEY` not informed. Any output will not be sent to Redis.")
    log(os.environ)

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', None)

if not REDIS_INPUT_KEY:
    log("Please inform `REDIS_INPUT_KEY` at .env file")
    exit(1)

HANDLER_FUNCTION_NAME = os.getenv('HANDLER_FUNCTION_NAME', None)

module_loader = importlib.util.find_spec('usermodule')
dir_module_loader = False
directory_path = '/runtime/user'

if os.path.isdir(directory_path):
    sys.path.append(directory_path)
    dir_module_loader = importlib.util.find_spec('mymodule')

if not module_loader and not dir_module_loader:
    log("neither `usermodule` or `user dir` found!")
    exit(1)
elif module_loader and dir_module_loader:
    log("finded both `usermodule` or `user dir`. Using files from `user dir`")

module_loader = dir_module_loader
handler = getattr(module_loader, HANDLER_FUNCTION_NAME, None)

if callable(handler):
    log("Environment is loaded. Starting Serverless function execution...")
else:
    log(f"Function '{HANDLER_FUNCTION_NAME}' not found in module '{module_loader}'.")
    exit(1)

from context import Context
context = Context(host=REDIS_HOST, port=REDIS_PORT,
                  input_key=REDIS_INPUT_KEY, output_key=REDIS_OUTPUT_KEY)
count = 0
while True:
    data = None
    output = None
    try:
        data = context.get_data()
    except:
        log("Data not available yet!")
        log(traceback.format_exc())
    
    if data:
       try:
           data = json.loads(data)
           output = handler(data, context)
       except:
            log("Error in Serverless function. Please check your `handler` method in usermodule.py")
            log(traceback.format_exc())

       try:
           if output:
               context.set_data(json.dumps(output))
           context.confirm_execution()
       except:
            log("Error while trying to save result")
            log(traceback.format_exc())
            
    count += 1
    time.sleep(context.monitoring_interval)
    
