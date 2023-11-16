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

class EventPublisher:
    # def __init__(self, modb, config, mq_host, get_mapPose):
    def __init__(self, mq_host, status_summary):
        # rm - mqtt
        # self.mq_publisher = mqtt.Client("event_publisher")
        # self.mq_publisher.connect(mq_host)
        self.status_summary = status_summary
        self.pos_x = 0
        self.pos_y = 0
        self.pos_theta = 0
        self.map_rm_guid = ''
        
        # self.get_mapPose = get_mapPose
        # yf config
        # self.robot = Robot.Robot(config, port_config, self.skill_config_path)
        # self.modb = MODB.robotDBHandler(config)

    def get_robot_summary(self):
        obj = json.loads(self.status_summary())
        pos_x = obj["position"]["x"]
        pos_y = obj["position"]["y"]
        pos_theta = obj["position"]["theta"]
        map_rm_guid = obj["map_rm_guid"]
        return (pos_x, pos_y, pos_theta, map_rm_guid)

    def get_robot_post(self):
        # self.pos_x = pos_x
        # self.pos_y = pos_y
        # self.pos_theta = pos_theta
        # self.map_rm_guid = map_rm_guid
        print(self.status_summary())
        obj = json.loads(self.status_summary())
        print(obj)
        self.pos_x = obj["position"]["x"]
        self.pos_y = obj["position"]["y"]
        self.pos_theta = obj["position"]["theta"]
        self.map_rm_guid = obj["map_rm_guid"]
        
    def set_robot_pose_xy(self, x,y):
        self.pos_x = x
        self.pos_y = y

    def start(self):
        # self.mq_publisher.loop_start()
        print(f'[event_handler]: Start...')

    # Event handler    
    def publish(self):
        print('[event_publisher.py] Event Publish')
        self.event = RMSchema.Event(self.title, self.severity , self.description, self.mapPose, self.medias).to_json()
        mq_publisher = mqtt.Client("event_publisher")
        mq_publisher.connect('localhost')
        mq_publisher.publish('/robot/event' , self.event)
        print(f"[event_publisher.py] {self.event}")
        event_id = json.loads(self.event)["eventId"]
        return event_id

    def add_title(self, title):
        self.title  = title
        
    def add_severity(self, severity):
        self.severity = severity
        
    def add_description(self, description):
        self.description = description
        
    def add_mapPose(self, x = -1, y = -1):
        self.get_robot_post()
        # set x,y if xy pos is given
        if x != -1 and y != -1:
            self.set_robot_pose_xy(x,y)
        self.mapPose = RMSchema.mapPose(x=self.pos_x, y=self.pos_y, heading=self.pos_theta, mapId=self.map_rm_guid)
        # self.mapPose = RMSchema.mapPose(mapId='277c7d6f-2041-4000-9a9a-13f162c9fbfc')
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
        self.add_medias(medias)
        
    def publish_test(self):
        self.add_title('event_test_rev06')
        self.add_severity(1)
        self.add_description('This is an event test')
        self.add_mapPose()
        self.add_empty_medias()

        self.publish()
        
if __name__ == "__main__":
    def status_summary():
            status = '{"battery": 97.996, "position": {"x": 105.40159891291846, "y": 67.38314149752657, "theta": 75.20575899303867}, "map_id": 2, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
            return status

    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../conf/port_config.properties')
    # modb = MODB.robotDBHandler(config)
    
    event_handler = EventPublisher("localhost", status_summary)
    event_handler.start()

    root_path = os.path.abspath('../../')
    event_path = os.path.join(root_path, "data/event-images")
    task_id = '20230331_145659_0001'
    img_name = 'front_right.png'
    event_img_path = os.path.join(event_path, task_id, img_name)
    event_img_path = event_img_path.replace("\\", "/") # for window

    # print(event_img_path)

    # to publish an event
    # 1. event title.   (str)
    # 2. severity.      (int) (1: critical 2: normal)
    # 3. description    (str) 
    # 4. mapPose_json   (str)
    # 5. medias_json    (str) (optional)
    # 6. metadata       (str) (optional)

    medias = []
    medias.append(RMSchema.Meida(event_img_path, 1, "Front Right"))

    event_handler.add_title('event_test_rev06')
    event_handler.add_severity(1)
    event_handler.add_description('This is an event test')
    event_handler.add_mapPose()
    event_handler.add_medias(medias)

    event_handler.publish()
    event_handler.publish()
    event_handler.publish()
    