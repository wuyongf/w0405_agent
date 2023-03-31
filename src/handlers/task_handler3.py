import os, sys
import time
import json
import paho.mqtt.client as mqtt
import threading 
# yf
import src.utils.methods as umethods
import src.models.robot as Robot
import src.models.db_robot as NWDB
import src.models.schema_rm as RMSchema
import src.models.enums_rm as RMEnum

class TaskHandler:
    def __init__(self, config, mq_host):
        # rm - mqtt
        self.mq_publisher = mqtt.Client("task_status_publisher")
        self.mq_publisher.connect(mq_host) 

        self.mq_subscriber = mqtt.Client("task_subscriber")      
        self.mq_subscriber.connect(mq_host)
        self.mq_subscriber.on_message = self.on_message

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
        threading.Thread(target=self.subscribe_task).start()   # from RV API
        print(f'[task_handler]: Start...')

    def subscribe_task(self):
        while True:
            self.mq_subscriber.subscribe("/rm/task", 2)
            time.sleep(1)
    
    # MQTT MECHANISM - The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")

        if msg.topic == '/rm/task':
            print("Exeucte Task...")        
            time.sleep(2)
            self.task_handler(str(msg.payload.decode("utf-8")))

    # Task status handler
    def task_status_callback(self, task_id, task_type, status = RMEnum.TaskStatusType):
        task_status_json = {
            "taskId": task_id,
            "taskType": task_type,
            "taskStatusType": status.value # 1. executing, 2. complete 3. failed
        }
        task_status_msg = json.dumps(task_status_json)
        self.mq_publisher.publish("/robot/task/status", task_status_msg)

    def task_handler(self, task):
        if task.scheduleType == 4: # Start
            self.execute_task(task)
            return
        if task.scheduleType == 3: # Resume
            self.robot.resume_current_task()
            return
        if task.scheduleType == 2: # Pause
            self.robot.pause_current_task()
            return
        if task.scheduleType == 1: # Abort
            self.robot.cancel_current_task()
            return

    def execute_task(self, task):
        task_json = json.loads(task)
        task = RMSchema.Task(json.loads(task))
        if task is None: return print('[execute_task] Error: RM task is not assign correctly')

        self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Executing)

        if task.taskType == 'RM-LOCALIZE':
            res = self.robot.localize(task_json)
            if(res): return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else: return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
            
        if task.taskType == 'RM-GOTO':
            res = self.robot.goto(task_json, self.task_status_callback)
            if(res): return
            else: return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
        
        if task.taskType == 'RV-LEDON':
            res = self.robot.led_on(task)
            if(res): return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else: return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
        
        if task.taskType == 'RV-LEDOFF':
            res = self.robot.led_off(task)
            if(res): return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else: return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
        
        if task.taskType == 'NW-BASIC-SLEEP1S':
            try:
                time.sleep(1)
                self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            except:
                print('[NW-BASIC-SLEEP1S] Error: Please check the workflow.')
                self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)

        
if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')
    task_handler = TaskHandler(config, "localhost")

    task_handler.start()