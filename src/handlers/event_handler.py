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

    def start(self):
        self.mq_publisher.loop_start()
        print(f'[event_handler]: Start...')

    # Event handler    
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

    # config = umethods.load_config('../../conf/config.properties')
    # event_handler = EventHandler(config, "localhost")
    # event_handler.start()

    root_path = os.path.abspath('../')
    event_path = os.path.join(root_path, "data/event_images")
    task_id = '20230331_145659_0001'
    img_name = 'front_right.png'
    event_img_path = os.path.join(event_path, task_id, img_name)
    event_img_path = event_img_path.replace("\\", "/") # for window

    print(event_img_path)

    # to publish an event
    # 1. event title.   (str)
    # 2. severity.      (int) (1: critical 2: normal)
    # 3. description    (str) 
    # 4. mapPose_json   (str)
    # 5. medias_json    (str) (optional)
    # 6. metadata       (str) (optional)

    # medias = []
    # medias.append(RMSchema.Meida(event_img_path, 1, "Front Right"))

    # event_handler.add_title('event_test_rev04')
    # event_handler.add_severity(1)
    # event_handler.add_description('This is an event test')
    # event_handler.add_mapPose()
    # event_handler.add_medias(medias)

    # event_handler.publish()