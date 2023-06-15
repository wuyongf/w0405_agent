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
    {'x': 438, 'y': 398.0},  # P1
    {'x': 456.0, 'y': 364.0}, # P2
    {'x': 493.0, 'y': 382.0}, # P3
    {'x': 475.0, 'y': 419.0},  # P4
]

robotStatusJson = {
    "batteryPct": 100.0,
    "mapPose": {
        "mapId": "1e28ee6e-2fc4-4d72-bed5-8d1a421783ff",
        "x": simPath[0]["x"],
        "y": simPath[0]["y"],
        "z": 0.0,
        "heading": 0.0
    },
    "state": 2
}

robotStatus = json.dumps(robotStatusJson)

publisher = mqtt.Client("publisher")
subscriber = mqtt.Client("subscriber")


def publishTExecuting(task_id, task_type):
    task_status_json = {
        "taskId": task_id,
        "taskType": task_type,
        "taskStatusType": 1
    }
    task_status_msg = json.dumps(task_status_json)
    publisher.publish("/robot/task/status", task_status_msg)

def publishTComplete(task_id, task_type):
    task_status_json = {
        "taskId": task_id,
        "taskType": task_type,
        "taskStatusType": 2
    }
    print("Publish Complete task...")
    task_status_msg = json.dumps(task_status_json)
    publisher.publish("/robot/task/status", task_status_msg)

def executeTask(task):
    global robotStatusJson
    task_json_object = json.loads(task)
    publishTExecuting(task_json_object["taskId"], task_json_object["taskType"])
    if task_json_object["taskType"] == 'RM-GOTO':        
        robotStatusJson['mapPose']['mapId'] = task_json_object["parameters"]['mapId']
        robotStatusJson['mapPose']['x'] = task_json_object["parameters"]['x']
        robotStatusJson['mapPose']['y'] = task_json_object["parameters"]['y']
        robotStatusJson['mapPose']['heading'] = 0
    publishTComplete(task_json_object["taskId"], task_json_object["taskType"])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    print("*******************************************************************************************************")
    print("message received ", str(msg.payload.decode("utf-8")))
    print("message topic=", msg.topic)
    print("*******************************************************************************************************")

    if msg.topic == '/rm/task':
        print("Exeucte Task...")        
        time.sleep(2)
        executeTask(str(msg.payload.decode("utf-8")))
        
if __name__ == "__main__":
    abspath = os.path.abspath(sys.argv[0])
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    publisher.connect("localhost")
    subscriber.connect("localhost")

    subscriber.on_message = on_message
    
    publisher.loop_start()
    subscriber.loop_start()

    while True:
        robotStatus = json.dumps(robotStatusJson)
        publisher.publish("/robot/status", robotStatus)
        subscriber.subscribe([("/robot/status", 0), ("/rm/task", 0), ("/robot/task/status", 0)])

        time.sleep(1)
