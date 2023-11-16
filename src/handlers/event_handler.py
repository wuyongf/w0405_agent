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
import src.models.db_robot as MODB
import src.models.schema.rm as RMSchema
import src.models.enums.rm as RMEnum

class EventHandler:
    def __init__(self, modb, config, mq_host, get_mapPose):
        # rm - mqtt
        self.mq_publisher = mqtt.Client("event_publisher")
        self.mq_publisher.connect(mq_host) 
        self.get_mapPose = get_mapPose
        # yf config
        # self.robot = Robot.Robot(config, port_config, self.skill_config_path)
        # self.modb = MODB.robotDBHandler(config)

    def start(self):
        self.mq_publisher.loop_start()
        print(f'[event_handler]: Start...')

    # Event handler    
    def publish(self):
        # self.event = RMSchema.EventWithoutMedia(self.title, self.severity , self.description, self.mapPose).to_json()
        self.event = RMSchema.Event(self.title, self.severity , self.description, self.mapPose, self.medias).to_json()
        self.mq_publisher.publish('/robot/event' , self.event)
        print(self.event)

    def publish_without_media(self):
        self.event = RMSchema.EventWithoutMedia(self.title, self.severity , self.description, self.mapPose).to_json()
        # self.event = RMSchema.Event(self.title, self.severity , self.description, self.mapPose, self.medias).to_json()
        self.mq_publisher.publish('/robot/event' , self.event)
        print(self.event)

    def add_title(self, title):
        self.title  = title
    def add_severity(self, severity):
        self.severity = severity
    def add_description(self, description):
        self.description = description
    def add_mapPose(self):
        self.mapPose = RMSchema.mapPose(mapId='1f7f78ab-5a3b-467b-9179-f7508a99ad6e')
        # self.mapPose = self.robot.get_current_mapPose()
        # self.mapPose = self.get_mapPose()
    def add_medias(self, medias):
        self.medias = medias
        
    def add_empty_medias(self):
        root_path = os.path.abspath('../../')
        event_path = os.path.join(root_path, "data/event-images")
        task_id = '20230331_145659_0001'
        img_name = 'front_right.png'
        event_img_path = os.path.join(event_path, task_id, img_name)
        event_img_path = event_img_path.replace("\\", "/") # for window
        medias = []
        medias.append(RMSchema.Meida(event_img_path, 1, "Front Right"))
        # medias.clear()
        self.add_medias(medias)
    
    def publish_test(self, title, description):
        self.add_title(f'{title}')
        self.add_severity(1)
        self.add_description(f'{description}')
        self.add_mapPose()
        self.add_empty_medias()

        self.publish()

    def publish_test(self, title, description):
        self.add_title(f'{title}')
        self.add_severity(1)
        self.add_description(f'{description}')
        self.add_mapPose()
        # self.add_empty_medias()

        self.publish_without_media()

if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../conf/port_config.properties')
    modb = MODB.robotDBHandler(config)

    event_handler = EventHandler(modb, config, "localhost", None)
    event_handler.start()

    # event_handler.add_empty_medias()
    event_handler.publish_test('AI Module Alert: Abnormal Lift Noise Detected!', 'Please check Mission 211 records for the details.')
    # root_path = os.path.abspath('../../')
    # event_path = os.path.join(root_path, "data/event-images")
    # task_id = '20230331_145659_0001'
    # img_name = 'front_right.png'
    # event_img_path = os.path.join(event_path, task_id, img_name)
    # event_img_path = event_img_path.replace("\\", "/") # for window

    # print(event_img_path)

    # to publish an event
    # 1. event title.   (str)
    # 2. severity.      (int) (1: critical 2: normal)
    # 3. description    (str) 
    # 4. mapPose_json   (str)
    # 5. medias_json    (str) (optional)
    # 6. metadata       (str) (optional)

    # medias = []
    # # medias.append(RMSchema.Meida(event_img_path, 1, "Front Right"))

    # event_handler.add_title('AI Module Alert: Abnormal Lift Noise Detected! Please Check Mission 211 Records for the details.')
    # event_handler.add_severity(1)
    # event_handler.add_description('...')
    # event_handler.add_mapPose()
    # event_handler.add_medias(medias)

    # event_handler.publish()
    
    # AI Module Alert: Abnormal Lift Noise Detected! Please Check Mission 211 Records for the details.
    # Sensor Value Alert: NW-CO2