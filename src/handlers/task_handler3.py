import os
import sys
import time
import json
import paho.mqtt.client as mqtt
import threading
import logging
# yf
import src.utils.methods as umethods
import src.models.robot as Robot
import src.models.db_robot as NWDB
import src.models.schema.rm as RMSchema
import src.models.enums.rm as RMEnum


class TaskHandler:
    def __init__(self, robot: Robot.Robot):
        # rm - mqtt
        self.publisher = mqtt.Client("task_status_publisher")
        self.publisher.connect("localhost")

        self.subscriber = mqtt.Client("task_subscriber")
        self.subscriber.connect("localhost")
        self.subscriber.on_message = self.on_message

        # yf config
        self.robot = robot
    
    def start(self):
        self.publisher.loop_start()
        self.subscriber.loop_start()
        threading.Thread(target=self.subscribe_task).start()   # from RV API
        print(f'[task_handler]: Start...')

    def subscribe_task(self):
        while True:
            self.subscriber.subscribe("/rm/task", 2)
            time.sleep(1)

    # MQTT MECHANISM - The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")

        if msg.topic == '/rm/task':
            print("task handler...")
            time.sleep(2)
            self.task_handler(str(msg.payload.decode("utf-8")))

    # Task status handler
    def task_status_callback(self, task_id, task_type, status=RMEnum.TaskStatusType):
        task_status_json = {
            "taskId": task_id,
            "taskType": task_type,
            "taskStatusType": status.value  # 1. executing, 2. complete 3. failed
        }
        task_status_msg = json.dumps(task_status_json)
        self.publisher.publish("/robot/task/status", task_status_msg)

    def task_handler(self, task_str):
        task = RMSchema.Task(json.loads(task_str))
        if task is None:
            return print('[task_handler] Error: RM task is not assign correctly')

        if task.scheduleType == 4:  # Start
            self.execute_task(task_str)
            return
        if task.scheduleType == 3:  # Resume
            self.robot.resume_current_task()
            # self.execute_task(task_str)
            return
        if task.scheduleType == 2:  # Pause
            self.robot.pause_current_task()
            return
        if task.scheduleType == 1:  # Abort
            self.robot.cancel_current_task()
            return

    def execute_task(self, task_str):
        task_json = json.loads(task_str)
        print(task_json['taskId'])
        try:
            task = RMSchema.Task(json.loads(task_str))
            if task is None:
                return print('[execute_task] Error: RM task is not assign correctly')
        except:
            return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)

        self.task_status_callback(
            task.taskId, task.taskType, RMEnum.TaskStatusType.Executing)

        if task.taskType == 'RM-LOCALIZE':
            res = self.robot.localize(task_json)
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)

        if task.taskType == 'RM-GOTO':
            res = self.robot.goto(task_json, self.task_status_callback)
            if (res):
                return
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)

        if task.taskType == 'RV-LEDON':
            res = self.robot.led_on(task)
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)

        if task.taskType == 'RV-LEDOFF':
            res = self.robot.led_off(task)
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
            
        if task.taskType == 'FUNC-LIFTLEVLLING':
            res = self.robot.inspect_lift_levelling(task_json)
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
            
        if task.taskType == 'FUNC-IAQ-ON':
            res = self.robot.iaq_on(task_json)
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
        
        if task.taskType == 'FUNC-IAQ-OFF':
            res = self.robot.iaq_off(task_json)
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
            
        if task.taskType == 'DELIVERY-CONFIGURATION':
            # res = self.robot.new_delivery_mission(task_json)
            # if (res):
            #     return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            # else:
            #     return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
            thread = threading.Thread(target=self.robot.delivery_mission_publisher)
            thread.start()
            return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            
        if task.taskType == 'DELIVERY-WAITLOADING':
            res = self.robot.wait_for_loading_package()
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)
            
        if task.taskType == 'DELIVERY-WAITUNLOADING':
            res = self.robot.wait_for_unloading_package()
            if (res):
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            else:
                return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)

        if task.taskType == 'NW-BASIC-SLEEP1S':
            try:
                time.sleep(1)
                self.task_status_callback(
                    task.taskId, task.taskType, RMEnum.TaskStatusType.Complete)
            except:
                print('[NW-BASIC-SLEEP1S] Error: Please check the workflow.')
                self.task_status_callback(
                    task.taskId, task.taskType, RMEnum.TaskStatusType.Fail)


if __name__ == "__main__":


    config = umethods.load_config('../../conf/config.properties')
    task_handler = TaskHandler(config)

    task_handler.start()
