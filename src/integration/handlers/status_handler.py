import threading
import time
import paho.mqtt.client as mqtt
import src.integration.models.rm.definition as rm_models
import src.integration.models.rv.definition as rv_models
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
import requests
import logging
import json
import src.integration.models.rv.api as rv_api

class StatusHandler:
    def __init__(self, config_addr, mq_host, mq_topic):
        self.mq_client = mqtt.Client("status_publisher")
        self.topic_name = mq_topic        
        self.mq_client.connect(mq_host)
        self.rvapi = rv_api.RVAPI(config_addr)
    
    def publish_status(self): 
        threading.Thread(target=self.__update_status).start()   # from RV API
        threading.Thread(target=self.__publish_status).start()  # to NCS

    def __update_status(self): # update thread
        # setup requests
        rm_mapPose = rm_models.MapPose('', 0, 0, 0)
        self.rm_status = rm_models.Status(0, 1, rm_mapPose)

        while True:
            try:
                # # rm status <--- rv status
                self.rm_status.batteryPct = round(self.rvapi.getBatteryState().percentage * 100, 3)  # battery
                self.rm_status.state = 1

                rm_mapPose.x = 0
                rm_mapPose.y = 0
                rm_mapPose.heading = 0

                rm_mapPose.mapId = self.rvapi.getPose().mapName        # mapPose
                # rm_mapPose.x = round(self.rvapi.getPose().x,3)
                # rm_mapPose.y = round(self.rvapi.getPose().y,3)
                # rm_mapPose.heading = abs(self.rvapi.getPose().angle)
                self.rm_status.mapPose = rm_mapPose

            except HTTPError as http_err:
                logging.getLogger('').exception(http_err)
            except ConnectionError as ce:
                logging.getLogger('').exception(ce)
            except Timeout:
                logging.getLogger('').error("Timeout session.get()")
                
            time.sleep(1.0)

    def __publish_status(self): # publish thread
        while True:  
            time.sleep(1)
            if self.rm_status.batteryPct == 0:
                continue
            json_status_str = json.dumps(self.rm_status.__dict__, default=lambda o: o.__dict__)
            print(json_status_str)
            self.mq_client.publish(self.topic_name, json_status_str)


# todo: 1. map coordinate transformation
#       2. rv amr status and ncs state
#       3. global map position.