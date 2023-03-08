#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Nicholas, NCS Product and Platforms, RobotManager
# Created Date: 22 Dec 2021
# version ='1.0'
# ---------------------------------------------------------------------------
"""Example client code to publish robot status to Robot Agent v2.0"""  
# ---------------------------------------------------------------------------
import time
import json
import paho.mqtt.client as mqtt
import random
from jproperties import Properties
import os
import sys 

simPath = [
    {'x': 778.0, 'y': 210.0},
    {'x': 1106.0, 'y': 520.0},
    {'x': 1114.0, 'y': 750.0},
    {'x': 726.0, 'y': 484.0}
]

robotStatusJson = {
    "batteryPct": 100.0,
    "mapPose": {
        "mapId": "817f100b-6dfb-4bca-9037-098f84d530e1",
        "x": 1076.0,
        "y": 456.0,
        "z": 0.0,
        "heading": 0.0
    },
    "state": 2
}

robotStatus = json.dumps(robotStatusJson)

def updateLocation(message):

    global robotStatus
    data = json.loads(robotStatus)
    json_object = json.loads(message)

    print(json_object["taskType"])

    publishTExecuting()
    data["mapVerID"] = json_object["point"]['mapVerID']
    data["positionX"] = json_object["point"]['x']
    data["positionY"] = json_object["point"]['y']
    status = json.dumps(data)
    publishTComplete()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    print("*******************************************************************************************************")
    print("message received ", str(msg.payload.decode("utf-8")))
    print("message topic=", msg.topic)
    print("*******************************************************************************************************")

    # if msg.topic == '/robot/task':
        
    #     # time.sleep(2)
    #     updateLocation(str(msg.payload.decode("utf-8")))
        
if __name__ == "__main__":
    abspath = os.path.abspath(sys.argv[0])
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    publisher = mqtt.Client("publisher")
    publisher.connect("localhost")
    subscriber = mqtt.Client("subscriber")
    subscriber.connect("localhost")

    subscriber.on_message = on_message

    i = 0

    # configs = Properties()
    # robotId = "664e0340-6f46-4872-b392-8b1a25dc324d"
    # try:
    #     with open('../../conf/rm/root-config.properties', 'rb') as config_file:
    #         configs.load(config_file)
    #         robotId = configs.get('robotId').data
    # except:
    #     print("Error loading properties file, make sure you key in correct directory")
            
    while True:

        publisher.loop_start()
        subscriber.loop_start()
        if i == len(simPath):
            i = 0
        robotStatusJson["mapPose"]["x"] = simPath[i]["x"]
        robotStatusJson["mapPose"]["y"] = simPath[i]["y"]

        robotStatusJson["batteryPct"] =round(random.uniform(0.0, 100.0), 2)
        robotStatus = json.dumps(robotStatusJson)
        publisher.publish("/robot/status", robotStatus)
        # subscriber.subscribe([("/robot/status", 0), ("/rm/task", 0), ("/robot/task/status", 0)])
        subscriber.subscribe([("/rm/task", 0), ("/robot/task/status", 0)])

        # publisher.loop_stop()
        # subscriber.loop_stop()

        time.sleep(1)
        i += 1
