import paho.mqtt.client as mqtt
import json
import time
import threading
# yf
import src.utils.methods as umethods
import src.models.api_rv as RVAPI

# workflow:
# 1. switch to manual mode
# 2. publish mqtt topic

class NWMQTTPub():
    def __init__(self, config):
        self.broker_address = config.get('IPC', 'localhost')
        self.broker_port = config.get('NWMQTT', 'port')
        self.robot_guid = config.get('NWDB', 'robot_guid')
        self.robot_id = config.get('NWDB', 'robot_id')
        self.nw_client = mqtt.Client("nw_mqtt_publisher")
        self.nw_client.on_message = self.__on_message
    
    def connect(self):
        self.nw_client.connect(self.broker_address, int(self.broker_port), 60)
        self.nw_client.loop_start()

    def start(self):
        self.connect()
        # self.subscribe()
        threading.Thread(target=self.__subscribe_task).start()
        print('[NWMQTT] Start...')

    def __subscribe_task(self):
        while True:
            time.sleep(1)

    def __on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        # self.__parse_message(msg)

    def fans_on(self, type):
        # Define topic and payload
        topic = "nw/set/fans"
        payload = {
            "set" : "on",
            "fan": f"{type}"
            }
        # Convert payload to JSON string
        payload_str = json.dumps(payload)
        # Publish message
        self.nw_client.publish(topic, payload_str)

    def fans_off(self, type):
        # Define topic and payload
        topic = "nw/set/fans"
        payload = {
            "set" : "off",
            "fan": f"{type}"
            }
        # Convert payload to JSON string
        payload_str = json.dumps(payload)
        # Publish message
        self.nw_client.publish(topic, payload_str)


if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')

    pub = NWMQTTPub(config)
    pub.start()

    pub.fans_off('all')
    time.sleep(2)
