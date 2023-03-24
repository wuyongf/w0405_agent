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
        # rm - mqtt
        self.mq_publisher = mqtt.Client("status_publisher")
        self.mq_topic_name = mq_topic        
        self.mq_publisher.connect(mq_host)
        # yf config
        self.robot = Robot.Robot(config)
        self.nwdb = NWDB.robotDBHandler(config)
        # rm status
        self.rm_mapPose = RMSchema.mapPose()
        self.rm_status  = RMSchema.Status(0.0, 0, self.rm_mapPose)
        # nwdb
        self.map_id = 0
    
    def start(self):
        self.mq_publisher.loop_start()
        threading.Thread(target=self.__update_status).start()   # from RV API
        threading.Thread(target=self.__publish_status).start()  # to rm and nwdb
        print(f'[status_handler]: Start...')

    def __update_status(self): # update thread
        while True:  
            try:
                # # rm status <--- rv statu
                self.rm_status.state = 1 # todo: robot status

                self.rm_mapPose.mapId = self.robot.get_current_map_rm_guid()    # map
                self.rm_status.batteryPct = self.robot.get_battery_state()      # battery
                pixel_x, pixel_y, heading = self.robot.get_current_pose()       # current pose
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
            print(f'[status_handler]: robot battery: {self.rm_status.batteryPct}')
            print(f'[status_handler]: robot map rm_guid: {self.rm_status.mapPose.mapId}')
            print(f'[status_handler]: robot position: ({self.rm_status.mapPose.x}, {self.rm_status.mapPose.y}, {self.rm_status.mapPose.heading})')
            
            try:
                json_data = json.dumps(self.rm_status.__dict__, default=lambda o: o.__dict__)
                # print(json_data)
                
                ## to rm
                self.mq_publisher.publish(self.mq_topic_name, json_data)
                ## to nwdb
                self.nwdb.update_robot_position(self.rm_status.mapPose.x, self.rm_status.mapPose.y, self.rm_status.mapPose.heading)
                self.nwdb.update_robot_map_id(self.map_id)
                self.nwdb.update_robot_battery(self.rm_status.batteryPct)
            except:
                print('[status_handler.__publish_status] Error. Plese Check')
            
if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    status_handler = StatusHandler(config, "localhost", "/robot/status")
    status_handler.start()