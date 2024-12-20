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
import src_mir.models.robot_mir as MiRRobot
import src.models.api_rv as RVAPI
import src.models.db_robot as NWDB
import src.models.schema.rm as RMSchema
import src.models.schema.rv as RVSchema
import src.models.enums.nw as NWEnum

class StatusHandler:
    def __init__(self, robot: MiRRobot.Robot):
        # rm - mqtt
        self.publisher = mqtt.Client("status_publisher")
        self.topic = "/robot/status"        
        self.publisher.connect("localhost")
        # yf config
        self.robot = robot

        # # nwdb
        # self.map_id = 0

    def start(self):
        # status
        self.publisher.loop_start()
        # threading.Thread(target=self.__update_status).start()   # from RV API
        threading.Thread(target=self.__publish_status).start()  # to rm and nwdb
        print(f'[status_handler]: Start...')

    def __update_status(self): # update thread
        while True:  
            try:

                pass
                # # # rm status <--- rv statu
                # self.rm_status.state = 1 # todo: robot status

                # self.rm_mapPose.mapId = self.robot.get_current_map_rm_guid()    # map
                # self.rm_status.batteryPct = self.robot.get_battery_state(NWEnum.Protocol.RVAPI)      # battery
                # pixel_x, pixel_y, heading = self.robot.get_current_pose(NWEnum.Protocol.RVAPI)       # current pose
                # # print(pixel_x, pixel_y, heading)
                # self.rm_mapPose.x = pixel_x
                # self.rm_mapPose.y = pixel_y
                # self.rm_mapPose.heading = heading

                # ## TO NWDB
                # self.map_id = self.robot.get_current_map_id()

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
            
            try:     
                # print(f'[status_handler]: robot battery: {self.robot.robot_status.batteryPct}')
                # print(f'[status_handler]: robot map rm_guid: {self.robot.robot_status.mapPose.mapId}')
                # print(f'[status_handler]: robot position: ({self.robot.robot_status.mapPose.x}, {self.robot.robot_status.mapPose.y}, {self.robot.robot_status.mapPose.heading})')
                       
                ## to rm
                self.publisher.publish(self.topic, self.robot.status.to_json())
                ## to nwdb
                self.robot.nwdb.update_robot_position(self.robot.status.layoutPose.x, self.robot.status.layoutPose.y, self.robot.status.layoutPose.heading)
                self.robot.nwdb.update_robot_map_id(self.robot.map_nw_id)
                self.robot.nwdb.update_robot_battery(self.robot.status.batteryPct)
                # self.robot.nwdb.update_robot_locker_status(self.robot.robot_locker_is_closed)
                # self.robot.nwdb.update_robot_status_mode(self.robot.mode)
            except:
                print('[status_handler.__publish_status] Error. Plese Check')

    def publish_status(self): # publish thread
        while True:  
            time.sleep(2)
            
            try:     
                print(f'[status_handler]: robot battery: {self.robot.status.batteryPct}')
                print(f'[status_handler]: robot map rm_guid: {self.robot.status.mapPose.mapId}')
                print(f'[status_handler]: robot position: ({self.robot.status.mapPose.x}, {self.robot.status.mapPose.y}, {self.robot.status.mapPose.heading})')
                       
                ## to rm
                self.publisher.publish(self.topic, self.robot.status.to_json())
                ## to nwdb
                self.robot.nwdb.update_robot_position(self.robot.status.mapPose.x, self.robot.status.mapPose.y, self.robot.status.mapPose.heading)
                self.robot.nwdb.update_robot_map_id(self.robot.map_nw_id)
                self.robot.nwdb.update_robot_battery(self.robot.status.batteryPct)

                ## robot-status-mode
                
            except:
                print('[status_handler.__publish_status] Error. Plese Check')
            
if __name__ == '__main__':
    config = umethods.load_config('../../conf/config_mir.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    robot = MiRRobot.Robot(config,port_config)
    robot.status_start()  
    status_handler = StatusHandler(robot)
    # status_handler.start()             
    
    status_handler.publish_status()