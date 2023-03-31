import os, sys
import time
import json
import paho.mqtt.client as mqtt
import threading
import logging
import uuid
# yf
import src.utils.methods as umethods
import src.models.robot as Robot
import src.models.db_robot as NWDB
import src.models.schema_rm as RMSchema
import src.models.enums_rm as RMEnum

class EventHandler:
    def __init__(self, config, mq_host):
        # rm - mqtt
        self.mq_publisher = mqtt.Client("event_publisher")
        self.mq_publisher.connect(mq_host) 

        # yf config
        self.robot = Robot.Robot(config)
        self.nwdb = NWDB.robotDBHandler(config)
        # rm status
        self.rm_mapPose = RMSchema.mapPose()
        self.rm_status  = RMSchema.Status(0.0, 0, self.rm_mapPose)
        # nwdb
        self.map_id = 0

    def start(self):
        self.mq_publisher.loop_start()
        print(f'[event_handler]: Start...')

    # Event handler
    def publish1(self, task_id, task_type, status = RMEnum.TaskStatusType):
        task_status_json = {
            "taskId": task_id,
            "taskType": task_type,
            "taskStatusType": status.value # 1. executing, 2. complete 3. failed
        }
        task_status_msg = json.dumps(task_status_json)
        self.mq_publisher.publish('/robot/event' , task_status_msg)
    
    def publish(self):
        self.event = RMSchema.Event(self.title, self.severity , self.description, self.mapPose, self.medias).to_json()
        self.mq_publisher.publish('/robot/event' , self.event)
        print(self.event)

    def add_title(self, title):
        self.title  = title
    def add_severity(self, severity):
        self.severity = severity
    def add_description(self, description):
        self.description = description
    def add_mapPose(self):
        # self.mapPose = RMSchema.mapPose()
        self.mapPose = self.robot.get_current_mapPose()
    def add_medias(self, medias):
        self.medias = medias
        
if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')
    event_handler = EventHandler(config, "localhost")
    event_handler.start()

    # to publish an event
    # 1. event title.   (str)
    # 2. severity.      (int) (1: critical 2: normal)
    # 3. description    (str) 
    # 4. mapPose_json   (str)
    # 5. medias_json    (str) (optional)
    # 6. metadata       (str) (optional)

    medias = RMSchema.Medias()
    medias.append(RMSchema.Meida("C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/front_right.png", 1, "Front Right"))

    event_handler.add_title('event_test_rev01')
    event_handler.add_severity(1)
    event_handler.add_description('This is an event test')
    event_handler.add_mapPose()
    event_handler.add_medias(medias)

    event_handler.publish()