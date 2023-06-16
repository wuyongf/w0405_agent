import os
import sys
import time
import json
import paho.mqtt.client as mqtt
import threading
import logging
import uuid

# yf
import src.utils.methods as umethods
import src.models.robot_neat as NeatRobot
import src.models.db_robot as NWDB
import src.models.schema.rm as RMSchema
import src.models.enums.rm as RMEnum
import src.models.enums.nw as NWEnum
import src.models.enums.rm_skill as RMSkillEnum

class TaskPublisher:
    def __init__(self, robot: NeatRobot.Robot):
        # rm - mqtt
        self.ipc_ip_addr = robot.ipc_ip_addr
        self.publisher = mqtt.Client("task_publisher")
        self.publisher.connect(self.ipc_ip_addr)

        # yf config
        self.robot = robot

    def start(self):
        self.publisher.loop_start()
        # threading.Thread(target=self.subscribe_task).start()   # from RV API
        print(f'[task_publisher]: Start...')

    def task_RM_GOTO(self, name, x, y, heading):
        task_type = "RM-GOTO"
        map_id = self.robot.robot_status.mapPose.mapId
        task_json = {
            "taskId": str(uuid.uuid1()),
            "taskType": task_type,
            "parameters": {
                "mapId": map_id,
                "positionName": name,
                "x": x,
                "y": y,
                "heading": heading
            }
        }
        # task = json.dumps(task_json)
        return task_json
    
    def task_RV_LEDON(self):
        task_type = "RV-LEDON"
        # map_id = self.robot.robot_status.mapPose.mapId
        task_json = {
            "taskId": str(uuid.uuid1()),
            "taskType": task_type,
            "parameters": {}
        }
        # task = json.dumps(task_json)
        return task_json
        pass


    def new_job(self, name, tasks):
        job_json = {
            "id": str(uuid.uuid1()), 
            "name": name,
            "tasks": tasks
        }
        job = json.dumps(job_json)

        self.publisher.publish('/robot/job/update', job)   
        time.sleep(0.02)   
        print('done!!')

if __name__ == "__main__":

    # # Loading config files
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')

    # Robot
    robot = NeatRobot.Robot(config, port_config)
    robot.status_start(NWEnum.Protocol.RVMQTT)

    task_publisher = TaskPublisher(robot)
    task_publisher.start()

    ### new job
    # goto_1 = task_publisher.task_RM_GOTO('Point A', 93.149, 71.384, 50)
    # tasks = [goto_1]
    led_on = task_publisher.task_RV_LEDON()
    tasks = [led_on]
    print(tasks)

    task_publisher.new_job('led_on', tasks)



    