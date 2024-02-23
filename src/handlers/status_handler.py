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
from multiprocessing import Process, shared_memory
import numpy as np

class StatusHandler:
    def __init__(self, robot: Robot.Robot):
        # rm - mqtt
        self.publisher = mqtt.Client("status_publisher")
        self.topic = "/robot/status"        
        self.publisher.connect("localhost")
        # yf config
        self.robot = robot
        self.shm_name = self.robot.shm.name

    def start(self):
        # status
        self.publisher.loop_start()
        # threading.Thread(target=self.__update_status).start()   # from RV API
        threading.Thread(target=self.__publish_status).start()  # to rm and nwdb 
        # threading.Thread(target=self.__publish_status_robotLayoutPose,args=()).start()
        Process(target=self.__publish_status_robotLayoutPose,args=(self.shm_name,)).start()
        print(f'[status_handler]: Start...')

    def __publish_status(self): # publish thread
        while True:  
            time.sleep(1)
            try:            
                ## to rm
                self.publisher.publish(self.topic, self.robot.status.to_json())
                ## to nwdb
                # self.robot.nwdb.update_robot_position(self.robot.status.layoutPose.x, self.robot.status.layoutPose.y, self.robot.status.layoutPose.heading)
                self.robot.nwdb.update_robot_map_id(self.robot.map_nw_id)
                self.robot.nwdb.update_robot_battery(self.robot.status.batteryPct)
                self.robot.nwdb.update_robot_locker_status(self.robot.robot_locker_is_closed)
                self.robot.nwdb.update_robot_status_mode(self.robot.mode)
            except:
                print('[status_handler.__publish_status] Error. Plese Check')
    
    # def __publish_status_robotLayoutPose(self, shm_name): # publish thread
    def __publish_status_robotLayoutPose(self): # publish thread
        while True:  
            time.sleep(0.1)
            try:
                ## to nwdb
                self.robot.nwdb.update_robot_position(self.robot.status.layoutPose.x, self.robot.status.layoutPose.y, self.robot.status.layoutPose.heading)
            except:
                print('[status_handler.__publish_status] Error. Plese Check')

    def __publish_status_robotLayoutPose2(self, shm_name): # publish thread
        existing_shm = shared_memory.SharedMemory(name=shm_name)
        self.robot_position = np.ndarray((3,), dtype=np.float32, buffer=existing_shm.buf)
        while True:  
            time.sleep(0.1)
            try:
                x = self.robot_position[1]
                y = self.robot_position[2]
                heading = self.robot_position[3]            
                ## to nwdb
                # print(self.robot_position)
                self.robot.nwdb.update_robot_position(x, y, heading)
            except:
                print('[status_handler.__publish_status] Error. Plese Check')

    def publish_status(self): # publish thread
        while True:  
            time.sleep(1)
            
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
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    robot = Robot.Robot(config,port_config)
    robot.status_start(NWEnum.Protocol.RVAPI)
    status_handler = StatusHandler(robot)
    # status_handler.start()             
    
    status_handler.publish_status()