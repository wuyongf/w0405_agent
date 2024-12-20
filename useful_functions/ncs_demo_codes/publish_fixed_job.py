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

if __name__ == "__main__":
    try: 
        logging.info("Connecting to MQTT: %s %d", mqtt_host, mqtt_port)
        client.connect(host=mqtt_host, port=mqtt_port)
        client.loop_start()

        """  Job update parameters (Example of robot going to Point A) """ 
        job_name = "GOTO Point A"
        task_type = "RM-GOTO"
        map_id = "d7355d44-df67-4d26-8d25-36928746b7ee"  # Replace it with actual value   
        position_name = "Point A"
        x = 1.0
        y = 1.0
        heading = 360

        job_guid =  '7856edc4-b5bc-11ed-8cfb-f426796b3c13'
        # task_guid = '7856edc5-b5bc-11ed-926c-f426796b3c13'
        task_guid = '4dd67a4c-f5da-4b51-938e-33e8a60d92d6'

        job_update_json = {
            "id": job_guid,
            "name": "GOTO Point A",
            "tasks": [{
                "taskId": task_guid,
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

        # """  Publish the job update to fleet agent """
        # if map_id == "":
        #     logging.fatal('Unable to run the script')
        #     logging.fatal('Please replace map_id with actual value')
        # else:
        #     job_update = json.dumps(job_update_json)
        #     logging.info("Publish Job Update Message, topic: {}, msg: {}".format(job_update_topic, job_update_json))
        #     client.publish(job_update_topic, job_update)
        #     time.sleep(0.1)

        # """ This section is to simulate robot executing the job in job update """
        task_id = task_guid
        task_status_json = {
            'taskId': task_id,
            'taskType': task_type,
            "errMsg": ''
        }

        # """ Publish the Executing task status """
        # task_status_json['taskStatusType'] = 1
        # task_status = json.dumps(task_status_json)
        # logging.info("Publish Task Status Message {}".format(task_status))
        # client.publish(task_status_topic, task_status ,qos)
        # time.sleep(5)   
        
        # # """ Publish the Completed task status """
        # task_status_json['taskStatusType'] = 2
        # task_status = json.dumps(task_status_json)
        # logging.info("Publish Task Status Message {}".format(task_status))
        # client.publish(task_status_topic, task_status ,qos)
        # time.sleep(2)

        # """ Publish the Failed task status """
        time.sleep(2)
        task_status_json['taskStatusType'] = 3
        task_status_json['errMsg'] = "Motors failure"
        task_status = json.dumps(task_status_json)
        logging.info("Publish Task Status Message {}".format(task_status))
        client.publish(task_status_topic, task_status ,qos)
        time.sleep(2)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: ending MQTT client")
        client.loop_stop()
        client.disconnect()


# workflow
# 1. post a new job. status --> scheduled
# 2. update job status. -> activate(1) or complete(2)
# 3. update job status2.-> fail(3) or abort(4)

# rv
# 1. post a mission
# 2. get mission status.
