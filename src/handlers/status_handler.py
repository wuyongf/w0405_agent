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
import src.models.schema.rm as RMSchema
import src.models.schema.rv as RVSchema
import src.models.enums.nw as NWEnum

class StatusHandler:
    def __init__(self, config, port_config):
        # rm - mqtt
        self.publisher = mqtt.Client("status_publisher")
        self.topic = "/robot/status"        
        self.publisher.connect("localhost")
        # yf config
        self.robot = Robot.Robot(config, port_config)
        self.nwdb = NWDB.robotDBHandler(config)
        # rm status
        self.rm_mapPose = RMSchema.mapPose()
        self.rm_status  = RMSchema.Status(0.0, 0, self.rm_mapPose)
        # nwdb
        self.map_id = 0

    def start(self):
        # status
        self.publisher.loop_start()
        threading.Thread(target=self.__update_status).start()   # from RV API
        threading.Thread(target=self.__publish_status).start()  # to rm and nwdb
        print(f'[status_handler]: Start...')

    def __update_status(self): # update thread
        while True:  
            try:
                # # rm status <--- rv statu
                self.rm_status.state = 1 # todo: robot status

                self.rm_mapPose.mapId = self.robot.get_current_map_rm_guid()    # map
                self.rm_status.batteryPct = self.robot.get_battery_state(NWEnum.Protocol.RVAPI)      # battery
                pixel_x, pixel_y, heading = self.robot.get_current_pose(NWEnum.Protocol.RVAPI)       # current pose
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
            time.sleep(2)
            print(f'[status_handler]: robot battery: {self.rm_status.batteryPct}')
            print(f'[status_handler]: robot map rm_guid: {self.rm_status.mapPose.mapId}')
            print(f'[status_handler]: robot position: ({self.rm_status.mapPose.x}, {self.rm_status.mapPose.y}, {self.rm_status.mapPose.heading})')
            
            try:                
                ## to rm
                self.publisher.publish(self.topic, self.rm_status.to_json())
                ## to nwdb
                self.nwdb.update_robot_position(self.rm_status.mapPose.x, self.rm_status.mapPose.y, self.rm_status.mapPose.heading)
                self.nwdb.update_robot_map_id(self.map_id)
                self.nwdb.update_robot_battery(self.rm_status.batteryPct)
            except:
                print('[status_handler.__publish_status] Error. Plese Check')
            
if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    status_handler = StatusHandler(config)
    status_handler.start()