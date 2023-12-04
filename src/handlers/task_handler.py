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
        
        if task.scheduleType == 1:  # Abort
            self.cancel_task(task_str)
            return
        if task.scheduleType == 2:  # Pause
            self.pause_task(task_str)
            return
        if task.scheduleType == 3:  # Resume
            self.resume_task(task_str)
            return
        if task.scheduleType == 4:  # Start
            self.execute_task(task_str)
            return

    def cancel_task(self, task_str):
        task_json = json.loads(task_str)
        print(f'[task_handler.cancel_task]: {task_json["taskId"]}')
        try:
            task = RMSchema.Task(json.loads(task_str))
            if task is None:
                return print('[execute_task] Error: RM task is not assign correctly')
        except:
            return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
        
        if task.taskType == 'CHARGING':
            self.robot.rv_charging_stop()
        else:
            self.robot.cancel_moving_task()
        pass

    def pause_task(self, task_str):
        task_json = json.loads(task_str)
        print(f'[task_handler.pause_task]: {task_json["taskId"]}')
        self.robot.rvapi.pause_robot_task()
        pass

    def resume_task(self, task_str):
        task_json = json.loads(task_str)
        print(f'[task_handler.resume_task]: {task_json["taskId"]}')
        self.robot.rvapi.resume_robot_task()
        pass

    def execute_task(self, task_str):
        task_json = json.loads(task_str)
        print(f'[task_handler.execute_task]: {task_json["taskId"]}')
        try:
            task = RMSchema.Task(json.loads(task_str))
            if task is None:
                return print('[execute_task] Error: RM task is not assign correctly')
        except:
            return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

        self.task_status_callback(
            task.taskId, task.taskType, RMEnum.TaskStatusType.Executing)
        
        match task.taskType:

            case 'RM-LOCALIZE':
                res = self.robot.localize(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'RM-GOTO':
                res = self.robot.goto(task_json, self.task_status_callback)
                if (res):
                    return 
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'NW-GOTO':
                res = self.robot.nw_goto(task_json, self.task_status_callback)
                if (res):
                    return 
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                            
            case 'RV-LEDON': 
                res = self.robot.led_on(task)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'RV-FOLLOWME-MODE':
                res = self.robot.follow_me_mode(task)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'RV-FOLLOWME-PAIR':
                res = self.robot.follow_me_pair(task)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'RV-FOLLOWME-UNPAIR':
                res = self.robot.follow_me_unpair(task)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
            
            case 'RV-LEDOFF':
                res = self.robot.led_off(task)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                    
            case 'IAQ-ON':
                res = self.robot.iaq_on(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'IAQ-OFF':
                res = self.robot.iaq_off(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

            case 'LIFT-LEVLLING':
                res = self.robot.inspect_lift_levelling(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
            
            case 'LIFT-VIBRATION-ON':  
                res = self.robot.lift_vibration_on(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)  

            case 'LIFT-VIBRATION-OFF':
                res = self.robot.lift_vibration_off()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'DELIVERY-CONFIGURATION':
                res = self.robot.get_available_delivery_mission()
                if (res):
                    threading.Thread(target=self.robot.delivery_mission_publisher).start()
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)  
                   
            case 'DELIVERY-LOADING-PACKAGE':
                res = self.robot.wait_for_loading_package()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'DELIVERY-UNLOADING-PACKAGE':
                res = self.robot.wait_for_unloading_package()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'RV-CHARGING-CONFIGURATION':
                res = True
                if (res):
                    threading.Thread(target=self.robot.charging_mission_publisher, args=(task_json, self.task_status_callback)).start()
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'RV-CHARGING-ON':
                print(f'RV-CHARGING-ON JSON: {task_json}')
                res = self.robot.rv_charging_start(task_json, self.task_status_callback)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
            
            case 'RV-CHARGING-OFF':
                print(f'RV-CHARGING-OFF JSON: {task_json}')
                res = self.robot.rv_charging_stop(task_json, self.task_status_callback)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

            case 'NW-LIFT-IN':
                print(f'NW-LIFT-IN JSON: {task_json}')
                res = self.robot.nw_lift_in(task_json, self.task_status_callback)
                if (res):
                    return
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

            case 'NW-LIFT-OUT':
                print(f'NW-LIFT-OUT JSON: {task_json}')
                res = self.robot.nw_lift_out(task_json, self.task_status_callback)
                if (res):
                    return
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

            case 'NW-LIFT-TO':
                print(f'NW-LIFT-TO JSON: {task_json}')
                res = self.robot.nw_lift_to(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

            case 'NW-LIFT-RELEASE':
                print(f'NW-LIFT-RELEASE JSON: {task_json}')
                res = self.robot.nw_lift_release()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'LIFT-NOISE-DETECT-START':
                print(f'LIFT-NOISE-DETECT-START JSON: {task_json}')
                res = self.robot.lift_noise_detect_start(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

            case 'LIFT-NOISE-DETECT-END':
                # print(f'LIFT-NOISE-DETECT-END JSON: {task_json}')
                res = self.robot.lift_noise_detect_end()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
            
            case 'LIFT-NOISE-DETECT-ANALYSIS':
                # print(f'LIFT-NOISE-DETECT-END JSON: {task_json}')
                res = self.robot.lift_noise_detect_analysis()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)

            case 'WATER-LEAKAGE-DETECT-START':
                print(f'WATER-LEAKAGE-DETECT-START JSON: {task_json}')
                res = self.robot.water_leakage_detect_start(task_json)
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
                
            case 'WATER-LEAKAGE-DETECT-END':
                # print(f'WATER-LEAKAGE-DETECT-END JSON: {task_json}')
                res = self.robot.water_leakage_detect_end()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)
            
            case 'WATER-LEAKAGE-DETECT-ANALYSIS':
                # print(f'WATER-LEAKAGE-DETECT-END JSON: {task_json}')
                res = self.robot.water_leakage_detect_analysis()
                if (res):
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Completed)
                else:
                    return self.task_status_callback(task.taskId, task.taskType, RMEnum.TaskStatusType.Failed)


if __name__ == "__main__":


    config = umethods.load_config('../../conf/config.properties')
    task_handler = TaskHandler(config)

    task_handler.start()
