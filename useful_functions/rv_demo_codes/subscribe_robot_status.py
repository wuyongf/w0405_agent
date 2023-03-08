#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Yongfeng, NW
# Created Date: 27 Jan 2023
# version ='1.0'
# ---------------------------------------------------------------------------
"""Example client code to subscribe robot status from RV API"""
# ---------------------------------------------------------------------------

# Python 3.9.15
# RestfulClient.py
import os
import requests
from requests.auth import HTTPDigestAuth
import json
from jproperties import Properties  # config file

# Load config file
rv_configs = Properties()
try:
    with open('../../conf/nw/rv-config.properties', 'rb') as config_file:
        rv_configs.load(config_file)
        # rv_ip_addr = rm_configs.get('ip_address').data  # to access the properties.
except:
    print("Error loading rv properties file, make sure you key in correct directory")

def get_RVBattery(rv_configs):

    prefixed_url = rv_configs.get('PrefixedURL').data
    headers = {"X-API-Key": rv_configs.get('X-API-Key').data}

    session = requests.Session()
    url = prefixed_url + 'api/battery/v1/state'
    response = session.get(url, headers=headers, verify=False)

    if (response.ok):
        # print(response.content) # returns bytes
        # print(response.text)  # returns string
        data = response.json()
        battery_percentage = data.get('percentage')
        return battery_percentage
    else:
        # If response code is not ok (200), print the resulting http error code with description
        response.raise_for_status()
        return -1

if __name__ == "__main__":
    battery = get_RVBattery(rv_configs)
    print(battery)

# todo: 1. load the config file
#       2. get the date from RV API
#       3. re-assembly as RM API
#       4. publish


