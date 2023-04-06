import time
import paho.mqtt.client as mqtt
import threading
import configparser  # config file

def load_config(config_addr):
        # Load config file
        configs = configparser.ConfigParser()
        try:
            configs.read(config_addr)
        except:
            print("Error loading properties file, check the correct directory")
        return configs

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
            # self.mq_subscriber.subscribe([("/robot/status", 2), ("/rm/task", 2), ("/robot/task/status", 2)])
            self.mq_subscriber.subscribe([("/rm/control", 2), ("/rm/task", 0), ("/robot/task/status", 0)])
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

    config = load_config('./config.properties')
    mq_logger = MQLOGGER(config, "localhost")

    mq_logger.start()