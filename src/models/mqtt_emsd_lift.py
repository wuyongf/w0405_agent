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

# robocore-keymap
keymap = {
    'none': [2, 10],  # Use a list to store multiple values
    'open': [0],
    'close':[1],
    '1/F':  [3],
    '2/F':  [4],
    '3/F':  [5],
    '4/F':  [6],
    '5/F':  [7],
    '6/F':  [8],
    '7/F':  [9],
    'G/F':  [11]}

class EMSDLift():
    def __init__(self, config):
        # Init1: Create MQTT client and connect to broker
        # lift cfg
        cfg_session = 'ROBOCORE_Lift'
        host  = config.get(cfg_session,'host')
        port =  config.get(cfg_session,'port')
        username =  config.get(cfg_session,'username')
        password =  config.get(cfg_session,'password')[1:-1]
        self.lift_id =   config.get(cfg_session,'lift_id')

        # lift mqtt from robocore
        self.client = mqtt.Client('emsd_lift')
        self.client.username_pw_set(username, password)
        self.client.tls_set()
        self.client.connect(host, int(port))
        self.client.on_message = self.__on_message
        
        topics = []
        topics.append([f'Lift_Robo/{self.lift_id}/Control_Panel/Lift_State',0])
        # topics.append([f'Lift_Robo/{lift_id}/Control_Panel/Key_Press',0])
        topics.append([f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Response',0])
        self.client.subscribe(topics)

        # lift properties
        self.occupied = False
        self.anykey_pressed = False
        self.indexes_of_pressed_key = []

        # lift status
        self.current_floor = ''

    def __subscribe_task(self):
        self.client.loop_start()
        while True:
            time.sleep(1)

    def start(self):
        threading.Thread(target=self.__subscribe_task).start()   # from RV API
        print('[EMSDLift] Start...')

    def __on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")
        self.__parse_message(msg)

    def __parse_message(self,msg):
        topic = msg.topic.split('/')[-1]
        msg_json =  json.loads(str(msg.payload.decode("utf-8")))
        # print(topic)
        if topic == 'Lift_State': 
            
            # update lift status
            self.current_floor = self.get_current_floor_from_keymap(msg_json['Lift_Floor'])
            print(f'current_floor: {self.current_floor}')
            # check if any key is pressed
            self.is_anykey_pressed(msg_json)
            pass

    def get_current_floor_from_keymap(self, Lift_Floor):
        target_value = []
        target_value.append(Lift_Floor)
        
        # Find the key that corresponds to the target value
        matching_keys = [key for key, value in keymap.items() if value == target_value]

        return matching_keys[0]

    ## lift methods
    def get_state(self):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = None, error_code = 240, Key_Press = []).to_json()
        self.client.publish(topic, msg)

    def release_all_keys(self):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = None, error_code = 241, Key_Press = []).to_json()
        self.client.publish(topic, msg)

    def to(self, floor_name, duration = 2):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = duration, error_code = 0, Key_Press = keymap['floor_name']).to_json()
        self.client.publish(topic, msg)
    
    def open(self, duration = 2):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = duration, error_code = 0, Key_Press = keymap['open']).to_json()
        self.client.publish(topic, msg)

    def close(self, duration = 2):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = duration, error_code = 0, Key_Press = keymap['close']).to_json()
        self.client.publish(topic, msg)

    def is_anykey_pressed(self, msg_json):

        # Given hex number
        hex_number = msg_json['Button_Bitmap']

        # Convert hex to binary
        binary_string = bin(int(hex_number[2:], 16))[2:]  # Remove '0b' prefix

        # Find all indexes of '1' bits (from right to left)
        self.indexes_of_pressed_key = [i for i, bit in enumerate(binary_string[::-1]) if bit == '1']

        if binary_string == '0' and self.indexes_of_pressed_key == []:
            self.anykey_pressed = False
            print(f'no key is pressed!')
        else:
            self.anykey_pressed = True
            # print("Binary representation:", binary_string)
            print("pressed key list:", self.indexes_of_pressed_key)
        pass

    def is_key_pressed(self, floor_name):
        self.get_state()
        if self.anykey_pressed:
            if keymap[floor_name][0] in self.indexes_of_pressed_key:
                return True
        return False

    def is_available(self):
        lift_state = []
        for i in range(6):
            self.get_state()
            if self.anykey_pressed: return False
            else: 
                lift_state.append(self.current_floor)
            time.sleep(1)
        return all(item == lift_state[0] for item in lift_state)


if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')

    lift = EMSDLift(config)
    lift.start()

    while(True):
        time.sleep(2)
        res = lift.is_available()
        print(f'lift.is_available: {res}')
        # res = lift.is_key_pressed("G/F")
        # if res:
        #     print(f'G/F is pressed!!!')
        # else:
        #     print(f'G/F is not pressed!!!')

    # time.sleep(5)
    # print(f'get current state...')
    # lift.get_state()
    # print(f'end...')

    # print(keymap['none'])  # Output: 0
    # print(keymap['3/F'])        # Output: 5
    # print(keymap['G/F'])  # Output: 11

    # # Given hex number
    # hex_number = "000000000000000000000000000000"

    # # Convert hex to binary
    # binary_string = bin(int(hex_number, 16))[2:]  # Remove '0b' prefix

    # # Find all indexes of '1' bits (from right to left)
    # indexes_of_ones = [i for i, bit in enumerate(binary_string[::-1]) if bit == '1']

    # print("Binary representation:", binary_string)
    # print("Indexes of '1' bits (from right to left):", indexes_of_ones)