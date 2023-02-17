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
import src.integration.models.rm.definition as rm_models

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
    logging.info("Connecting to MQTT: %s %d", mqtt_host, mqtt_port)
    client.connect(host=mqtt_host, port=mqtt_port)
    client.loop_start()

    """  Job update parameters (Example of robot going to Point A) """
    # init - task_param
    map_id = "a41c914e-9097-41cb-9b4b-60fc8da8d66a"
    # init - task
    task_type = "RM-GOTO"
    task_id = str(uuid.uuid1())
    # init - job
    job_name = 'GOTO Point A'
    job_id = str(uuid.uuid1())

    # construct task_param, task, and job
    tasks = []
    task_param = rm_models.RMGOTO(map_id, 'PointA', 1.0, 1.0, 360)
    task1 = rm_models.Task1(task_id, task_type, task_param)
    task2 = rm_models.Task2(task_id,4,2,task_type,task_param)
    tasks.append(task2)
    job = rm_models.JobUpdate(job_id, job_name, tasks)

    job_update_json = json.dumps(job.__dict__, default=lambda o: o.__dict__)

    """  Publish the job update to fleet agent """
    if map_id == "":
        logging.fatal('Unable to run the script')
        logging.fatal('Please replace map_id with actual value')
    else:
        logging.info("Publish Job Update Message, topic: {}, msg: {}".format(job_update_topic, job_update_json))
        client.publish(job_update_topic, job_update_json)
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
