import paho.mqtt.client as mqtt
import json
import time
import threading
from multiprocessing import Process
# yf
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
from src.utils import get_unix_timestamp
import src.models.schema.robocore_lift as LiftSchema
# workflow:
# 1. switch to manual mode
# 2. publish mqtt topic

# robocore-keymap
keymap_robocore_nw = {
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

keymap_nw_rm = {
    '1/F':  1,
    '2/F':  2,
    '3/F':  3,
    '4/F':  4,
    '5/F':  5,
    '6/F':  6,
    '7/F':  7,
    'G/F':  0}

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
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.tls_set()
        self.client.connect(host, int(port))

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # lift properties & status
        self.occupied = True
        self.anykey_pressed = True
        self.pressed_key_robocore = []
        self.current_floor_str = 'G/F'
        self.pressed_floorkey_nw_rm = []

        # for ncs integration
        self.rm_current_floor = 0
        self.rm_destination_floor = 0
        self.rm_motion_state = 0
        self.rm_door_state = 0
        self.rm_available_modes = [0]
        self.rm_current_mode = 0

    def update_motion_state(self):

        # init
        self.pressed_floorkey_nw_rm.clear()

        # robocore key to nw_rm
        for target_value in self.pressed_key_robocore:
            if(target_value == 0 or 1 or 2 or 10): continue
            else:
                matching_keys = [key for key, value in keymap_robocore_nw.items() if value == target_value]
                self.pressed_floorkey_nw_rm.append(keymap_nw_rm[matching_keys])

        print(self.pressed_floorkey_nw_rm)

        pass

    def on_connect(self, client, userdata, flags, rc):
        # print("Connected with result code " + str(rc))

        '''Subscribe to the topics when connected'''
        topics = []
        topics.append([f'Lift_Robo/{self.lift_id}/Control_Panel/Lift_State',0])
        # topics.append([f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press',0])
        # topics.append([f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Response',0])
        
        self.client.subscribe(topics)
        pass
    
    def on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        # print("*******************************************************************************************************")
        # print("message received ", str(msg.payload.decode("utf-8")))
        # print("message topic=", msg.topic)
        # print("*******************************************************************************************************")
        self.parse_message(msg)
        pass

    def parse_message(self,msg):
        topic = msg.topic.split('/')[-1]
        msg_json =  json.loads(str(msg.payload.decode("utf-8")))
        # print(topic)
        if topic == 'Lift_State': 
            
            # update lift status
            self.current_floor_str = self.__get_current_floor_from_keymap(msg_json['Lift_Floor'])
            self.rm_current_floor = keymap_nw_rm[f'{self.current_floor_str}']
            # print(f'current_floor: {self.current_floor}')

            # check if any key is pressed
            self.func_is_anykey_pressed(msg_json)

            # door status
            if(self.is_key_pressed("open")): self.rm_door_state = 2
            else: self.rm_door_state = 0

            pass

    def start(self):
        threading.Thread(target=self.subscribe_task).start()
        threading.Thread(target=self.thread_check_is_available).start()
        print('[EMSDLift] Start...')

    def subscribe_task(self):
        self.client.loop_start()
        while True:
            time.sleep(1)

    def __get_current_floor_from_keymap(self, Lift_Floor):
        target_value = []
        target_value.append(Lift_Floor)    
        # Find the key that corresponds to the target value
        matching_keys = [key for key, value in keymap_robocore_nw.items() if value == target_value]
        return matching_keys[0]

    ## lift methods
    def request_state(self):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = None, error_code = 240, Key_Press = []).to_json()
        self.client.publish(topic, msg)
        # time.sleep(1)

    def get_state(self):
        print(f'*****************')
        # print(f'[lift_state] is_anykey_pressed: {self.anykey_pressed}')
        print(f'[lift_state] pressed_key_robocore: {self.pressed_key_robocore}')
        print(f'[lift_state] current_floor_str: {self.current_floor_str}')
        print(f'[lift_state] is_availble: {not self.occupied}')
        print(f'[rm_lift_state] current_floor: {self.rm_current_floor}')
        print(f'[rm_lift_state] door_state: {self.rm_door_state}')
        print(f'*****************')

    def release_all_keys(self):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = None, error_code = 241, Key_Press = []).to_json()
        self.client.publish(topic, msg)

    def to(self, floor_name, duration = 2):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = duration, error_code = 0, Key_Press = keymap_robocore_nw[f'{floor_name}']).to_json()
        self.client.publish(topic, msg)

        time.sleep(1)
        self.request_state()
        print(f'self.pressed_key_robocore: {self.pressed_key_robocore}')
        print(keymap_robocore_nw[f'{floor_name}'])
        if(self.pressed_key_robocore == keymap_robocore_nw[f'{floor_name}']): return True
        return False
    
    def rm_to(self, floor_int, duration = 2):
        try:
            floor_name = list(keymap_nw_rm.keys())[list(keymap_nw_rm.values()).index(floor_int)]
            print(f'[rm_to] floor_name: {floor_name}')
            
            topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
            msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = duration, error_code = 0, Key_Press = keymap_robocore_nw[f'{floor_name}']).to_json()
            self.client.publish(topic, msg)

            time.sleep(1)
            self.request_state()
            if(keymap_robocore_nw[f'{floor_name}'][0] in self.pressed_key_robocore): 
                print(f'[lift.rm_to] this key is in the pressed key list!')
                return True
            return False
        except:
            print(f'[lift.rm_to] failed')
            return False  
        
    def open(self, duration = 10):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = duration, error_code = 0, Key_Press = keymap_robocore_nw['open']).to_json()
        self.client.publish(topic, msg)

        time.sleep(1)
        self.request_state()
        # print(f'self.pressed_key_robocore: {self.pressed_key_robocore}')
        # print(keymap_robocore_nw['open'])
        if(keymap_robocore_nw['open'][0] in self.pressed_key_robocore): return True
        return False

    def close(self, duration = 10):
        topic = f'Lift_Robo/{self.lift_id}/Control_Panel/Key_Press'
        msg = LiftSchema.Message(timestamp = get_unix_timestamp(), Press_Time = duration, error_code = 0, Key_Press = keymap_robocore_nw['close']).to_json()
        self.client.publish(topic, msg)

        time.sleep(1)
        self.request_state()
        # print(f'self.pressed_key_robocore: {self.pressed_key_robocore}')
        # print(keymap_robocore_nw['close'])
        if(self.pressed_key_robocore == keymap_robocore_nw['close']): return True
        return False

    def func_is_anykey_pressed(self, msg_json):

        # Given hex number
        hex_number = msg_json['Button_Bitmap']

        # Convert hex to binary
        binary_string = bin(int(hex_number[2:], 16))[2:]  # Remove '0b' prefix

        # Find all indexes of '1' bits (from right to left)
        self.pressed_key_robocore = [i for i, bit in enumerate(binary_string[::-1]) if bit == '1']

        if binary_string == '0' and self.pressed_key_robocore == []:
            self.anykey_pressed = False
            # print(f'no key is pressed!')
        else:
            self.anykey_pressed = True
            # print("Binary representation:", binary_string)
            # print("pressed key list:", self.indexes_of_pressed_key)
        pass

    def is_anykey_pressed(self):
        self.request_state()
        time.sleep(0.2)
        if self.anykey_pressed: return True
        return False

    def is_key_pressed(self, floor_name):
        self.request_state()
        if self.anykey_pressed:
            if keymap_robocore_nw[floor_name][0] in self.pressed_key_robocore:
                return True
        return False

    def thread_check_is_available(self):
        while(True):
            time.sleep(1)

            self.occupied = not self.is_available()
            # self.occupied = not is_available
    
    def is_available(self):
        lift_state = []
        
        for i in range(15):
            self.request_state()
            if self.anykey_pressed: 
                self.occupied = True
                return False
            else: 
                lift_state.append(self.current_floor_str)
            time.sleep(0.1)
        
        is_free = all(item == lift_state[0] for item in lift_state)
        
        self.occupied = not is_free
        return is_free
    
    def is_arrived(self, target_floor_int):
        
        if((self.rm_current_floor == target_floor_int) and (not self.occupied)): return True
        
        return False
        


if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')

    lift = EMSDLift(config)
    
    lift.start()

    # hold_min = 5
    # lift.open(10 * 60 * hold_min) 

    while(True):
        time.sleep(2)
        lift.get_state()
        lift.release_all_keys()
        res = lift.occupied
        print(res)
        # lift.update_motion_state()
        # res = lift.is_available()
        # print(f'lift.is_available: {res}')


        # res = lift.is_key_pressed("open")
        # if res:
        #     print(f'the key is pressed!!!')
        # else:
        #     print(f'the key is not pressed!!!')

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

    # lift is stop
    # 1. no key is pressed.
    # 2. 