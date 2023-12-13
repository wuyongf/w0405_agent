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
    def __init__(self, mq_host, status_summary):
        # rm - mqtt
        self.mq_publisher = mqtt.Client("event_publisher")
        self.mq_publisher.connect(mq_host) 
        self.status_summary = status_summary

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

    def add_mapPose(self, is_current_pos=True, pos_x=None, pos_y=None, pos_theta=None, map_rm_guid=None):
        if(is_current_pos):
            pos_x, pos_y, pos_theta, map_rm_guid = self.get_robot_post()

        self.mapPose = RMSchema.mapPose(x=pos_x, y=pos_y, heading=pos_theta, mapId=map_rm_guid)
    
    def get_robot_post(self):
        obj = json.loads(self.status_summary())
        pos_x = obj["position"]["x"]
        pos_y = obj["position"]["y"]
        pos_theta = obj["position"]["theta"]
        map_rm_guid = obj["map_rm_guid"]

        return pos_x, pos_y, pos_theta, map_rm_guid
    
    
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
    
    def publish_medias(self, title, description, medias):
        self.add_title(f'{title}')
        self.add_severity(1)
        self.add_description(f'{description}')
        # self.add_mapPose()
        self.add_medias(medias)
        self.publish()

    def publish_plain_text(self, title, description):
        self.add_title(f'{title}')
        self.add_severity(1)
        self.add_description(f'{description}')
        # self.add_mapPose()
        # self.add_empty_medias()

        self.publish_without_media()

if __name__ == "__main__":

    def status_summary():
            status = '{"battery": 97.996, "position": {"x": 105.40159891291846, "y": 67.38314149752657, "theta": 75.20575899303867}, "map_id": 2, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
            return status
    
    event_handler = EventHandler("localhost", status_summary)
    event_handler.start()
    
    # event_handler.add_mapPose(is_current_pos=True)
    # event_handler.add_mapPose(is_current_pos=False, pos_x=105.401, pos_y=67.3831, pos_theta=75.2057, map_rm_guid="277c7d6f-2041-4000-9a9a-13f162c9fbfc")
    # event_handler.publish_plain_text('AI Module Alert2: Abnormal Lift Noise Detected!', 
    #                                  'Please check Mission 211 records for the details.')
    medias = []
    medias.append(RMSchema.Meida('/home/nw/Documents/GitHub/w0405_agent/src/../results/water-leakage/thermal-image/20231213/321/2023_12_13_17_56_37_4.0_1320.517578125_259.02630615234375.jpg', 1, "Ceiling"))
    # event_handler.add_mapPose(is_current_pos=True)
    event_handler.add_mapPose(is_current_pos=False, pos_x=284.262, pos_y=1073.061, pos_theta=0, map_rm_guid="c5f360ec-f4be-4978-a281-0a569dab1174")
    event_handler.publish_medias('demo','....',medias)