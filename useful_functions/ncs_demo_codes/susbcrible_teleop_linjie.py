#!/usr/bin/env python3  
# Created By  : Lee Lin Jie
# Created Date: 20 Apr 2023
# Code extended from published_robot_status.py

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
        "mapId": "d7355d44-df67-4d26-8d25-36928746b7ee",
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

# ***** TODO ******
# teleoperation state is initialized as false here
# May need to retrive the state from robotmanager?
# ***** TODO ******
teleoperation = False


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
    publishTComplete(task_json_object["taskId"], task_json_object["taskType"])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    print("*******************************************************************************************************")
    print("message received ", str(msg.payload.decode("utf-8")))
    print("message topic=", msg.topic)
    print("*******************************************************************************************************")


def on_message_task(client, userdata, msg):
    print("Exeucte Task...")
    time.sleep(2)
    executeTask(str(msg.payload.decode("utf-8")))

def on_message_status(client, userdata, msg):
    pass

def on_message_mode(client, userdata, msg):
    print("Received Teleoperation mode change!")
    teleoperation = bool(json.loads(msg.payload)["teleoperation"])
    print(teleoperation)

def on_message_move(client, userdata, msg):
    if teleoperation == True:
        print("Recevied Move Command!")
        print(msg.payload)
        #----------------------------------------
        # Insert Robot Code here to make it move
        #----------------------------------------
    else:
        print("Teleoperation Mode is not enabled.")

if __name__ == "__main__":
    abspath = os.path.abspath(sys.argv[0])
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    
    publisher.connect("localhost")
    subscriber.connect("localhost")

    subscriber.on_message = on_message

    # Subscribe List of Topic
    subscriber.subscribe("/rm/task", qos=2)
    subscriber.subscribe("/rm/mode", qos=2)
    subscriber.subscribe("/rm/move", qos=0)
    subscriber.subscribe("/robot/status", qos=0)
    

    # Add topic callback
    subscriber.message_callback_add("/rm/task", on_message_task)
    subscriber.message_callback_add("/rm/mode", on_message_mode)
    subscriber.message_callback_add("/rm/move", on_message_move)
    subscriber.message_callback_add("/robot/status", on_message_status)
    

    i = 0


    
    publisher.loop_start()
    subscriber.loop_start()

    while True:
        robotStatus = json.dumps(robotStatusJson)
        publisher.publish("/robot/status", robotStatus)
        subscriber.subscribe([("/robot/status", 0), ("/rm/task", 0), ("/robot/task/status", 0)])

        time.sleep(1)
