import os
import sys
import time
import json
import paho.mqtt.client as mqtt
import threading 
# yf
import src.utils.methods as umethods
import src.models.robot as Robot
import src.models.api_rv as RVAPI
import src.models.db_robot as NWDB
import src.models.schema_rm as RMSchema
import src.models.schema_rv as RVSchema

class TaskHandler:
    def __init__(self, config, mq_host, subs_topic, pub_topic):
        # rm - mqtt
        self.mq_publisher = mqtt.Client("task_status_publisher")
        self.mq_publisher.connect(mq_host) 
        self.mq_pub_topic = pub_topic

        self.mq_subscriber = mqtt.Client("task_subscriber")
        self.mq_subs_topic = subs_topic       
        self.mq_subscriber.connect(mq_host)
        self.mq_subscriber.on_message = self.__on_message

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
        self.mq_subscriber.loop_start()
        threading.Thread(target=self.__subscribe_task).start()   # from RV API
        print(f'[task_handler]: Start...')

    def __subscribe_task(self):
        while True:
            # publisher.publish("/robot/status", robotStatus)
            # self.mq_subscriber.subscribe([("/robot/status", 0), ("/rm/task", 0), ("/robot/task/status", 0)])
            self.mq_subscriber.subscribe(self.mq_subs_topic, 2)
            time.sleep(1)
    
    # MQTT MECHANISM - The callback for when a PUBLISH message is received from the server.
    def __on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")

        if msg.topic == '/rm/task':
            print("Exeucte Task...")        
            time.sleep(2)
            self.__execute_task(str(msg.payload.decode("utf-8")))

    # Task status handler
    def __publish_task_executing(self, task_id, task_type):
        task_status_json = {
            "taskId": task_id,
            "taskType": task_type,
            "taskStatusType": 1
        }
        task_status_msg = json.dumps(task_status_json)
        self.mq_publisher.publish(self.mq_pub_topic, task_status_msg)

    def __publish_task_complete(self, task_id, task_type):
        task_status_json = {
            "taskId": task_id,
            "taskType": task_type,
            "taskStatusType": 2
        }
        print("Publish Complete task...")
        task_status_msg = json.dumps(task_status_json)
        self.mq_publisher.publish(self.mq_pub_topic, task_status_msg)

    def __publish_task_failed(self, task_id, task_type):
        task_status_json = {
            "taskId": task_id,
            "taskType": task_type,
            "taskStatusType": 3
        }
        print("task failed...")
        task_status_msg = json.dumps(task_status_json)
        self.mq_publisher.publish(self.mq_pub_topic, task_status_msg)

    def __execute_task(self, task):
        task_json = json.loads(task)
        task = RMSchema.Task(json.loads(task))
        if task is None: return print('[__execute_task] Error: RM task is not assign correctly')
             
        self.__publish_task_executing(task.taskId, task.taskType)
        
        if task.taskType == 'RM-LOCALIZE':
            res = self.robot.localize(task_json)
            if(res): return self.__publish_task_complete(task.taskId, task.taskType)
            else: return self.__publish_task_failed(task.taskId, task.taskType)
            
        if task.taskType == 'RM-GOTO':
            res = self.robot.goto(task_json)
            if(res): return self.__publish_task_complete(task.taskId, task.taskType)
            else: return self.__publish_task_failed(task.taskId, task.taskType)
        
        if task.taskType == 'RV-LEDON':
            res = self.robot.led_on(task)
            if(res): return self.__publish_task_complete(task.taskId, task.taskType)
            else: return self.__publish_task_failed(task.taskId, task.taskType)
        
        if task.taskType == 'RV-LEDOFF':
            res = self.robot.led_off(task)
            if(res): return self.__publish_task_complete(task.taskId, task.taskType)
            else: return self.__publish_task_failed(task.taskId, task.taskType)
        
        if task.taskType == 'NW-BASIC-SLEEP1S':
            try:
                time.sleep(1)
                self.__publish_task_complete(task.taskId, task.taskType)
            except:
                print('[NW-BASIC-SLEEP1S] Error: Please check the workflow.')
                self.__publish_task_failed(task.taskId, task.taskType)

        # self.__publish_task_complete(task.taskId, task.taskType)
        
if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')
    task_handler = TaskHandler(config, "localhost", "/rm/task", "/robot/task/status")

    task_handler.start()

    
