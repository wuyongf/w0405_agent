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



class EMSDLift():
    def __init__(self, config):
        # Init1: Create MQTT client and connect to broker
        # lift cfg
        host  = config.get('EMSD','host')
        port =  config.get('EMSD','port')
        username =  config.get('EMSD','username')
        password =  config.get('EMSD','password')[1:-1]
        lift_id = config.get('EMSD','lift_id')
        # lift mqtt
        self.client = mqtt.Client('emsd_lift')
        self.client.username_pw_set(username, password)
        self.client.tls_set()
        self.client.connect(host, int(port))
        self.client.on_message = self.__on_message

        topics = []
        topics.append([f'Lift_Robo/{lift_id}/Control_Panel/Lift_State',0])
        topics.append([f'Lift_Robo/{lift_id}/Control_Panel/Key_Press',0])
        topics.append([f'Lift_Robo/{lift_id}/Control_Panel/Key_Response',0])
        self.client.subscribe(topics)

        self.client.loop_start()

    def __on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")
        # self.__parse_message(msg)

    def __subscribe_task(self):
        while True:
            time.sleep(1)

    def start(self):
        threading.Thread(target=self.__subscribe_task).start()   # from RV API
        print('[EMSDLift] Start...')



if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')

    # lift = EMSDLift(config)
    # lift.start()

    keymap = {
    'none': [2, 10],  # Use a list to store multiple values
    'open': [0],
    'close':[1],
    '1/F': [3],
    '2/F': [4],
    '3/F': [5],
    '4/F': [6],
    '5/F': [7],
    '6/F': [8],
    '7/F': [9],
    'G/F': [11]
    }

    print(keymap['none'])  # Output: 0
    # print(value_map['3/F'])        # Output: 5
    # print(value_map['Ground floor'])  # Output: 11
