#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Goh Kae Yan, NCS Product and Platforms, RobotManager
# Created Date: 20 Dec 2022
# version ='1.0'
# ---------------------------------------------------------------------------
"""Example client code to publish job update to Fleet Agent v2.0"""  
# ---------------------------------------------------------------------------
import time
import json
import paho.mqtt.client as mqtt
import logging
import uuid

logging.basicConfig(format='%(asctime)s - line:%(lineno)d - %(levelname)s - %(message)s',level=logging.DEBUG)

"""  Config for MQTT connection """  
client_name = 'Job Update'
mqtt_host = 'localhost'
mqtt_port = 1883
job_update_topic = '/robot/job/update' 
task_status_topic = '/robot/task/status'
qos = 2   
client = mqtt.Client(client_name)

def postJob():
    pass

if __name__ == "__main__":

    logging.info("Connecting to MQTT: %s %d", mqtt_host, mqtt_port)
    client.connect(host=mqtt_host, port=mqtt_port)
    client.loop_start()

    """  Job update parameters (Example of robot going to Point A) """
    job_name = "GOTO Point A"
    task_type = "RM-GOTO"
    map_id = "a41c914e-9097-41cb-9b4b-60fc8da8d66a"  # Replace it with actual value
    position_name = "Point A"
    x = 1.0
    y = 1.0
    heading = 360

    job_update_json = {
        "id": str(uuid.uuid1()),
        "name": "GOTO Point A",
        "tasks": [{
            "taskId": str(uuid.uuid1()),
            "taskType": task_type,
            "parameters": {
                "mapId": map_id,
                "positionName": "PointA",
                "x": 1.0,
                "y": 1.0,
                "heading": 360
            }
        }]
    }

    """  Publish the job update to fleet agent """
    if map_id == "":
        logging.fatal('Unable to run the script')
        logging.fatal('Please replace map_id with actual value')
    else:
        job_update = json.dumps(job_update_json)
        logging.info("Publish Job Update Message, topic: {}, msg: {}".format(job_update_topic, job_update_json))
        client.publish(job_update_topic, job_update)
        time.sleep(0.02)

    # """ This section is to simulate robot executing the job in job update """
    # """ Publish the Executing task status """
    # """ TODO: Reuse the `fleet_task.py` logic """
    # task_id = job_update_json["tasks"][0]["taskId"]
    # task_status_json = {
    #     'taskId': task_id,
    #     'taskType': task_type,
    # }
    # task_status_json['taskStatusType'] = 1
    # task_status = json.dumps(task_status_json)
    # logging.info("Publish Task Status Message {}".format(task_status))
    # client.publish(task_status_topic, task_status ,qos)
    # time.sleep(5)
    #
    # """ Publish the Completed task status """
    # task_status_json['taskStatusType'] = 2
    # task_status = json.dumps(task_status_json)
    # logging.info("Publish Task Status Message {}".format(task_status))
    # client.publish(task_status_topic, task_status ,qos)
    # time.sleep(2)
