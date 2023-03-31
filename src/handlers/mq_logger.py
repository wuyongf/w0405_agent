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

class MQLOGGER:
    def __init__(self, config, mq_host):
        # rm - mqtt
        self.mq_subscriber = mqtt.Client("task_subscriber")    
        self.mq_subscriber.connect(mq_host)
        self.mq_subscriber.on_message = self.__on_message

    def start(self):
        self.mq_subscriber.loop_start()
        threading.Thread(target=self.__subscribe_task).start()   

    def __subscribe_task(self):
        while True:
            # publisher.publish("/robot/status", robotStatus)
            self.mq_subscriber.subscribe([("/robot/status", 2), ("/rm/task", 2), ("/robot/task/status", 2)])
            # self.mq_subscriber.subscribe(self.mq_subs_topic, 2)
            time.sleep(1)
    
    # MQTT MECHANISM - The callback for when a PUBLISH message is received from the server.
    def __on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")
        
if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')
    mq_logger = MQLOGGER(config, "localhost")

    mq_logger.start()

    
