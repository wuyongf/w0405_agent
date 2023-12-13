import time
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import json
import src.utils.methods as umethods
import src.top_module.io_module.sfp_actuator as SurfaceProActuator
import src.top_module.io_module.fans as Fans
import src.top_module.io_module.servo_motor as ServoMotor
import src.top_module.module.locker as Locker


class NWMQTT():
    def __init__(self, config, port_config):
        self.broker_address = config.get('IPC', 'localhost')
        self.broker_port = 1884
        self.robot_guid = config.get('NWDB', 'robot_guid')
        self.robot_id = config.get('NWDB', 'robot_id')
        self.nw_client = mqtt.Client("nw_mqtt_subscriber")
        self.nw_client.on_message = self.__on_message

        # self.subscriber.on_message = self.__on_message
        self.surface_actuator = SurfaceProActuator.sfp_actuator(port_config)
        self.fan = Fans.fans(port_config)
        self.servo_motor = ServoMotor.ServoMotor(port_config)
        self.lock = Locker.Locker(port_config)

    def connect(self):
        self.nw_client.connect(self.broker_address, self.broker_port, 60)
        self.nw_client.loop_start()

    def start(self):
        self.connect()
        self.subscribe()
        threading.Thread(target=self.__subscribe_task).start()
        print('[NWMQTT] Start...')
        # publish.single("nw/status/ui_status", json.dumps({"robot_guid": self.robot_guid, "result":{"ui_status": 1}}), qos=1, hostname="localhost", port=1884)

    def subscribe(self, qos=0):
        topic = 'nw/#'
        self.nw_client.subscribe(topic, qos=2)

    def __on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        # print("message received ", str(msg.payload.decode("utf-8")))
        # print("message topic=", msg.topic)
        self.__parse_message(msg)

    def __parse_message(self, msg):
        try:
            topic = msg.topic
            data = json.loads(str(msg.payload.decode("utf-8")))
            print()
            if topic.startswith('nw/set'):
                self.set_handler(topic, data)

            if topic.startswith('nw/get'):
                self.get_handler(topic, data)

        except:
            print('error')

    def __subscribe_task(self):
        while True:
            time.sleep(1)

    def set_handler(self, topic, data):
        set_action = data['set']

        if topic == 'nw/set/surface-actuator':
            if set_action == 'up' or set_action == 'down':
                self.surface_actuator.action(set_action)

        if topic == 'nw/set/lock':
            if set_action == 'unlock':
                self.lock.unlock()

        if topic == 'nw/set/servo-motor':
            if set_action == 'rotate':
                self.servo_motor.servo_flip(duration=0.2)

        if topic == 'nw/set/fans':
            if set_action == 'on' or set_action == 'off':
                if data['fan'] == 'iaq':
                    self.fan.iaq_fan(set_action)
                elif data['fan'] == 'cooling':
                    self.fan.cooling_fan(set_action)
                elif data['fan'] == 'all':
                    self.fan.all_fan(set_action)

    def get_handler(self, topic, data):
        get_status = None
        topic_publish = None

        if topic == 'nw/get/robot_id':
            topic_publish = 'robot_id'
            # print('getting the status of robot_id, True')
            get_status = {'robot_guid': self.robot_guid, 'robot_id': self.robot_id}

        if topic == 'nw/get/lock':
            if self.lock.is_closed() == True:
                print('getting the status of lock, True')
                get_status = 'Locked'
            if self.lock.is_closed() == False:
                print('getting the status of lock, False')
                get_status = 'unlocked'

        payload = {"robot_guid": self.robot_guid, "result": get_status}

        payload_json = json.dumps(payload)

        if get_status:
            if topic_publish:
                self.nw_client.publish(f'nw/status/{topic_publish}', payload_json)
            else:
                self.nw_client.publish('nw/status/', payload_json)


if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    nwmq = NWMQTT(config, port_config)
    # nwmq.connect()
    nwmq.start()



'''back up'''
# import time
# import threading
# import paho.mqtt.client as mqtt
# import paho.mqtt.publish as publish
# import json
# import src.utils.methods as umethods
# import src.top_module.io_module.sfp_actuator as SurfaceProActuator
# import src.top_module.io_module.fans as Fans
# import src.top_module.io_module.servo_motor as ServoMotor
# import src.top_module.module.locker as Locker

# class NWMQTT():
#     def __init__(self, config, port_config):
#         self.broker_address = config.get('IPC','localhost')
#         self.broker_port = 1884
#         self.robot_guid = config.get('NWDB', 'robot_guid')
#         self.robot_id = config.get('NWDB', 'robot_id')
#         self.nw_client = mqtt.Client("nw_mqtt_subscriber")
#         self.nw_client.on_message = self.__on_message
    
#         # self.subscriber.on_message = self.__on_message
#         self.surface_actuator = SurfaceProActuator.sfp_actuator(port_config)
#         self.fan = Fans.fans(port_config)
#         self.servo_motor = ServoMotor.ServoMotor(port_config)
#         self.lock = Locker.Locker(port_config)

#     def connect(self):
#         self.nw_client.connect(self.broker_address, self.broker_port, 60)
#         self.nw_client.loop_start()

#     def start(self):
#         self.connect()
#         self.subscribe()
#         threading.Thread(target=self.__subscribe_task).start()
#         print('[NWMQTT] Start...')
#         # publish.single("nw/status/ui_status", json.dumps({"robot_guid": self.robot_guid, "result":{"ui_status": 1}}), qos=1, hostname="localhost", port=1884)

#     def subscribe(self, qos=0):
#         topic = 'nw/#'
#         self.nw_client.subscribe(topic, qos=2)

#     def __on_message(self, client, userdata, msg):
#         # print(msg.topic+" "+str(msg.payload))
#         print("message received ", str(msg.payload.decode("utf-8")))
#         print("message topic=", msg.topic)
#         self.__parse_message(msg)

#     def __parse_message(self, msg):
#         try:
#             get_status = None
#             topic_publish = None
            
#             topic = msg.topic
#             data = json.loads(str(msg.payload.decode("utf-8")))
#             #Surface-actuator
#             if topic == 'nw/get/surface-actuator':
#                 print('')
#                 # get_status = surface_actuator.status
#             if topic == 'nw/set/surface-actuator':
#                 if data['set'] == 'up':
#                     self.surface_actuator.action(data['set'])
#                 if data['set'] == 'down':
#                     self.surface_actuator.action(data['set'])

#             if topic == 'nw/get/robot_id':
#                 topic_publish = 'robot_id'
#                 print('getting the status of lock, True')
#                 get_status = {'robot_guid': self.robot_guid, 'robot_id': self.robot_id}

#             #Lock        
#             if topic == 'nw/get/lock':
#                 if self.lock.is_closed() == True:
#                     print('getting the status of lock, True')
#                     get_status ='Locked'
#                 if self.lock.is_closed() == False:
#                     print('getting the status of lock, False')
#                     get_status ='unlocked'
#             if topic == 'nw/set/lock':
#                 if data['set'] == 'unlock':
#                     self.lock.unlock()
            
#             #Servo-motor
#             if topic == 'nw/get/servo-motor':
#                 print('')
#                 # get_status = servo-motor.status
#             if topic == 'nw/set/servo-motor':
#                 print(data['set'])
#                 if data['set'] == 'rotate':
#                     self.servo_motor.servo_flip(duration=0.2)
        
#             #Laser-actuator
#             # if topic == 'nw/get/laser-actuator':
#             #     print('')
#             #     # get_status = laser-actuator.status
#             # if topic == 'nw/set/laser-actuator':
#             #     print(data['set'])
#             #     if data['set'] == 'extract':
#             #         pass
#             #     if data['set'] == 'retract':
#             #         pass
#             #     if data['set'] == 'stop':
#             #         pass

#             payload = {
#                 "robot_guid": self.robot_guid,
#                 "result": get_status
#             }

#             payload_json = json.dumps(payload)

#             if get_status:
#                 if topic_publish:
#                     self.nw_client.publish(f'nw/status/{topic_publish}', payload_json)
#                 else:
#                     self.nw_client.publish('nw/status/', payload_json)
                    
#         except: print('error')
        
#     def __subscribe_task(self):
#         while True:
#             time.sleep(1)

# if __name__ == '__main__':
#     config = umethods.load_config('../../conf/config.properties')
#     port_config = umethods.load_config('../../conf/port_config.properties')
#     nwmq = NWMQTT(config, port_config)
#     # nwmq.connect()
#     nwmq.start()