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
import src.utils.methods as umethods
import src.models.robot as Robot
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
        self.robot = Robot.Robot(config)
        self.rvapi = RVAPI.RVAPI(config)
        self.nwdb = NWDB.robotDBHandler(config)
        # rm status
        self.rm_mapPose = RMSchema.mapPose()
        self.rm_status  = RMSchema.Status(0.0, 0, self.rm_mapPose)
    
    def publish_status(self): 
        threading.Thread(target=self.__update_status).start()   # from RV API
        threading.Thread(target=self.__publish_status).start()  # to rm and nwdb

    def __update_status(self): # update thread
        while True:  
            try:
                # # rm status <--- rv statu
                self.rm_status.state = 1 # todo: robot status

                self.rm_mapPose.mapId = self.robot.get_current_map_rm_guid()    # map
                
                self.rm_status.batteryPct = self.robot.get_battery_state()      # battery
                pixel_x, pixel_y, heading = self.robot.get_current_pose()   # current pose
                # print(pixel_x, pixel_y, heading)
                self.rm_mapPose.x = pixel_x
                self.rm_mapPose.y = pixel_y
                self.rm_mapPose.heading = heading

                ## TO NWDB
                self.map_id = self.robot.get_current_map_id()

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
            self.nwdb.update_robot_map_id(self.map_id)
            self.nwdb.update_robot_battery(self.rm_status.batteryPct)  # to nwdb

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    sh = StatusHandler(config, "localhost", "/robot/status")
    sh.publish_status()