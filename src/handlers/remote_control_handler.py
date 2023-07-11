#!/usr/bin/env python3  
# Created By  : Lee Lin Jie
# Created Date: 20 Apr 2023
# Code extended from published_robot_status.py

import time
import json
import paho.mqtt.client as mqtt
import random
from jproperties import Properties
import os, sys 
import threading 
# yf
import src.utils.methods as umethods
import src.models.robot as Robot
import src.models.db_robot as NWDB
import src.models.schema.rm as RMSchema
import src.models.enums.rm as RMEnum
import src.models.mqtt_rv_joystick as RVJoyStick

class RemoteControlHandler:
    def __init__(self, robot: Robot.Robot):
        # RM-MQTT
        self.subscriber = mqtt.Client("remote_control_subscriber")
        self.subscriber.connect('localhost') 

        self.subscriber.subscribe("/rm/mode", qos=2)
        self.subscriber.subscribe("/rm/move", qos=0)

        # Add topic callback
        self.subscriber.message_callback_add("/rm/mode", self.on_message_mode)
        self.subscriber.message_callback_add("/rm/move", self.on_message_move)

        # RV-Joystick
        self.joystick = robot.rvjoystick

        # # yf config
        # self.robot = Robot.Robot(config)
        # self.nwdb = NWDB.robotDBHandler(config)

        self.teleoperation = False

    def start(self):
        self.subscriber.loop_start()
        threading.Thread(target=self.subscribe_remote_control).start()   # from RV API
        print(f'[remote_control_handler]: Start...')

    def subscribe_remote_control(self):
        while True:
            # self.mq_subscriber.subscribe("/rm/task", 2)
            time.sleep(1)

    def on_message_mode(self, client, userdata, msg):
        print("[remote_control_handler]: Received Teleoperation mode change!")
        self.teleoperation = bool(json.loads(msg.payload)["teleoperation"])
        if(self.teleoperation == True):self.joystick.enable()
        else: self.joystick.disable()
        print(self.teleoperation)

    def on_message_move(self, client, userdata, msg):
        if self.teleoperation == True:
            # print("[remote_control_handler]: Recevied Move Command!")
            # print(msg.payload)

            #----------------------------------------
            # Insert Robot Code here to make it move
            #----------------------------------------
            # convert the value from RM to RV
            x = - json.loads(msg.payload)["x"]/100.0
            y = json.loads(msg.payload)["y"]/100.0
            # RM: y: -100, 100 down up 
            #     x: -100, 100 left, right
            # RV: -1,1
            self.joystick.move(y,x)

        else:
            print("Teleoperation Mode is not enabled.")

if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')
    remote_control_handler = RemoteControlHandler(config)
    remote_control_handler.start()