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

import requests
from requests.auth import HTTPDigestAuth
import json
from jproperties import Properties  # config file

import src.integration.models.rv.definition as rv_models

class RVAPI:
    def __init__(self, file_addr):
        self.configs = self._load_configs(file_addr)

    def _load_configs(self, file_addr):
        # Load config file
        configs = Properties()
        try:
            with open(file_addr, 'rb') as config_file:
                configs.load(config_file)
                # rv_ip_addr = rm_configs.get('ip_address').data
        except:
            print("Error loading rv properties file, make sure you key in correct directory")

        return configs

    def getBatteryState(self):
        prefixed_url = self.configs.get('PrefixedURL').data
        headers = {"X-API-Key": self.configs.get('X-API-Key').data}

        session = requests.Session()

        url = prefixed_url + 'api/battery/v1/state'

        response = session.get(url=url, headers=headers, verify=False)

        if (response.ok):
            # print(response.text)  # returns string

            # 1. get raw data
            data = response.json()
            # 2. return predefined object
            return rv_models.BatteryState(data)
        else:
            # If response code is not ok (200), print the resulting http error code with description
            response.raise_for_status()

    def getPose(self):
        prefixed_url = self.configs.get('PrefixedURL').data
        headers = {"X-API-Key": self.configs.get('X-API-Key').data}

        session = requests.Session()

        url = prefixed_url + 'api/localization/v1/pose'

        response = session.get(url, headers=headers, verify=False)

        if (response.ok):
            # print(response.text)  # returns string

            # 1. get raw data
            data = response.json()
            # 2. return predefined object
            return rv_models.Pose(data)
        else:
            # If response code is not ok (200), print the resulting http error code with description
            response.raise_for_status()

    def postMission(self, mission_id):
        prefixed_url = self.configs.get('PrefixedURL').data
        headers = {"X-API-Key": self.configs.get('X-API-Key').data}

        session = requests.Session()
        url = prefixed_url + 'api/mission/v1/execution/' + mission_id

        response = session.post(url, headers=headers, verify=False)
        response.raise_for_status()

    def postMQTT(self, topic_id, payload):
        prefixed_url = self.configs.get('PrefixedURL').data
        headers = {"X-API-Key": self.configs.get('X-API-Key').data}

        session = requests.Session()
        url = prefixed_url + 'api/mqtt/v1/publisher?topicId=' + topic_id + "&payload=" + payload

        response = session.post(url, headers=headers, verify=False)
        response.raise_for_status()

    def putLEDON(self, bool):
        prefixed_url = self.configs.get('PrefixedURL').data
        headers = {"X-API-Key": self.configs.get('X-API-Key').data}

        session = requests.Session()
        url = ''
        if(bool):
            url = prefixed_url + 'api/led/v1/ON'
        else:
            url = prefixed_url + 'api/led/v1/OFF'

        response = session.put(url, headers=headers, verify=False)
        response.raise_for_status()

if __name__ == "__main__":

    rvapi = RVAPI('../../../../conf/rv/rv-config.properties')

    print(rvapi.getBatteryState().percentage)   # yf_test: get rv battery
    print(rvapi.getPose().angle)                # yf_test: get rv pose
    # rvapi.postMission('12W238-TEST01')          # yf_test: post rv mission
    rvapi.putLEDON(1)

    # # yf_test: post rv mqtt/joystick
    # obj_joystick = rv_models.MQTTObjJoyStick(0, 1, False)
    # mqtt_joystick = rv_models.MQTTJoyStick(obj_joystick)
    #
    # json_payload = json.dumps(mqtt_joystick.__dict__, default=lambda o: o.__dict__)
    # print(json_payload)
    #
    # rvapi.postMQTT('joystick', json_payload)

# todo: 1. load the config file
#       2. get the date from RV API
#       3. re-assembly as RM API
#       4. publish


