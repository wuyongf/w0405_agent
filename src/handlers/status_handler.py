import threading
import time
import paho.mqtt.client as mqtt
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
import requests
import logging
import json
# yf
import src.models.api_rv as RVAPI
import src.models.db_robot as NWDB
import src.models.schema_rm as RMSchema
import src.models.schema_rv as RVSchema

class StatusHandler:
    def __init__(self, config, mq_host, mq_topic):
        self.mq_client = mqtt.Client("status_publisher")
        self.topic_name = mq_topic        
        self.mq_client.connect(mq_host)
        # yf config
        self.rvapi = RVAPI.RVAPI(config)
        self.nwdb = NWDB.robotDBHandler(config)
    
    def publish_status(self): 
        threading.Thread(target=self.__update_status).start()   # from RV API
        threading.Thread(target=self.__publish_status).start()  # to rm and nwdb

    def __update_status(self): # update thread
        while True:
            rv_mapName = self.rvapi.get_current_pose().mapName
            self.rv_battery = self.rvapi.get_battery_state()
            self.rv_pos = self.rvapi.get_current_pose()
            rm_mapPose = RMSchema.mapPose()
            self.rm_status  = RMSchema.Status(0.0, 0, rm_mapPose)
            try:
                # # rm status <--- rv status
                self.rm_status.batteryPct = round(self.rv_battery.percentage * 100, 3)  # battery
                self.rm_status.state = 1
                rm_mapPose.x = self.rv_pos.x
                rm_mapPose.y = self.rv_pos.y
                rm_mapPose.heading = abs(self.rv_pos.angle)
                rm_mapPose.mapId = rv_mapName       # mapPose
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
            print(self.rm_status.batteryPct)
            # if self.rm_status.batteryPct == 0:
            #     continue
            json_data = json.dumps(self.rm_status.__dict__, default=lambda o: o.__dict__)
            # print(json_data)
            self.mq_client.publish(self.topic_name, json_data)       # to rm
            self.nwdb.update_robot_position(self.rm_status.mapPose.x, self.rm_status.mapPose.y, self.rm_status.mapPose.heading)     # to nwdb
            self.nwdb.update_robot_battery(self.rm_status.batteryPct)  # to nwdb

# todo: 1. map coordinate transformation
#       2. rv amr status and ncs state
#       3. global map position.