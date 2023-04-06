#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#-----------------------------------------------------------------------------------------
# Created By  : Goh Kae Yan, NCS Product and Platforms, RobotManager
# Created Date: 31 May 2021
# version ='1.0'
# ----------------------------------------------------------------------------------------
"""Example client code to subcribe other telerobotics control from Robot Agent v2.0"""  
# ----------------------------------------------------------------------------------------
import paho.mqtt.client as mqtt
from types import SimpleNamespace
import json
import os

def on_message(client, userdata, msg):
    print("Received teleoperation control: ", str(msg.payload.decode("utf-8")))

    dict = json.loads(str(msg.payload.decode("utf-8")), object_hook=lambda d: SimpleNamespace(**d))
    if dict.controlType == 2:   # 2: Play Media (Image/Audio/Video)
        print("Playing media file: " + dict.parameters[1].value)
        noOfTimes = dict.parameters[2].value
        while noOfTimes > 0:            
            os.system("start " + dict.parameters[1].value)
            noOfTimes = noOfTimes - 1

if __name__ == "__main__":
    subscriber = mqtt.Client("subscriber")
    subscriber.connect("localhost")
    subscriber.on_message = on_message
    subscriber.subscribe("/rm/control")
    subscriber.loop_forever()