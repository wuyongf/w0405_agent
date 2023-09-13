import paho.mqtt.client as mqtt
import json
import time
import threading
# yf
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
from src.utils import get_unix_timestamp
import src.models.schema.robocore_lift as LiftSchema
# workflow:
# 1. switch to manual mode
# 2. publish mqtt topic

class EMSDLift():
    def __init__(self, config):
        # Init1: Create MQTT client and connect to broker
        # lift cfg
        cfg_session = 'ROBOCORE_Lift'
        self.host  = config.get(cfg_session,'host')
        self.port =  config.get(cfg_session,'port')
        username =  config.get(cfg_session,'username')
        password =  config.get(cfg_session,'password')[1:-1]
        self.lift_id =   config.get(cfg_session,'lift_id')

        # lift mqtt from robocore
        self.client = mqtt.Client('emsd_lift')
        self.client.username_pw_set(username, password)
        self.client.tls_set()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.host, int(self.port))

        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribe to the topic when connected
        topic = 'Lift_Robo/000000002E52810B/Control_Panel/Lift_State'
        self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")
        pass


if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')

    lift = EMSDLift(config)

    while(True):
        time.sleep(2)
        # lift.get_state()
