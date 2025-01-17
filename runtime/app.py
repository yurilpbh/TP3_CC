# -*- coding: utf-8 -*-

import traceback
import datetime
import json
import pandas as pd
import redis
import os
import importlib
import time

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

REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', 'metrics')

if not REDIS_INPUT_KEY:
    log("Please inform `REDIS_INPUT_KEY` at .env file")
    exit(1)

module_loader = importlib.util.find_spec('usermodule')

if not module_loader:
    log("`usermodule` not found!")
    exit(1)

import usermodule as lf

log("Environment is loaded. Starting Serverless function execution...")

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
           output = lf.handler(data, context)
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
    
