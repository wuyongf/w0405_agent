import time
import threading
import paho.mqtt.client as mqtt
import json
import src.utils.methods as umethods
import src.top_module.io_module.sfp_actuator as SurfaceProActuator
import src.top_module.io_module.fans as Fans

class NWMQTT():
    def __init__(self, config, port_config):
        # self.broker_address = config.get('IPC','localhost')
        self.robot_id = config.get('NWDB', 'robot_guid')
        self.broker_address = '192.168.0.18'
        self.broker_port = 1884
        self.nw_client = mqtt.Client("nw_mqtt_subscriber")
        self.nw_client.on_message = self.__on_message
    
        # self.subscriber.on_message = self.__on_message
        self.surface_actuator = SurfaceProActuator(port_config)
        self.fan = Fans(port_config)

    def connect(self):
        self.nw_client.connect(self.broker_address, self.broker_port, 60)
        self.nw_client.loop_start()

    def start(self):
        self.connect()
        self.subscribe()
        threading.Thread(target=self.__subscribe_task).start()
        print('[NWMQTT] Start...')

    def subscribe(self, qos=0):
        topic = 'nw01/#'
        self.nw_client.subscribe(topic, qos=2)

    def __on_message(self, client, userdata, msg):
        # print(msg.topic+" "+str(msg.payload))
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        self.__parse_message(msg)

    def __parse_message(self, msg):
        get_status = None
        topic = msg.topic
        data = json.loads(str(msg.payload.decode("utf-8")))
        #Surface-actuator
        if topic == 'nw01/get/surface-actuator':
            print('')
            # get_status = surface_actuator.status
        if topic == 'nw01/set/surface-actuator':
            if data['set'] == 'up':
                self.surface_actuator.action(data['set'])
            if data['set'] == 'down':
                self.surface_actuator.action(data['set'])

        #Lock        
        if topic == 'nw01/get/lock':
            print('')
            # get_status = lock.status
        if topic == 'nw01/set/lock':
            if data['set'] == 'unlock':
                pass
        
        #Servo-motor
        if topic == 'nw01/get/servo-motor':
            print('')
            # get_status = servo-motor.status
        if topic == 'nw01/set/servo-motor':
            print(data['set'])
            if data['set'] == 'rotate':
                pass

        #Servo-motor
        # if topic == 'nw01/get/laser-actuator':
        #     print('')
        #     # get_status = laser-actuator.status
        # if topic == 'nw01/set/laser-actuator':
        #     print(data['set'])
        #     if data['set'] == 'extract':
        #         pass
        #     if data['set'] == 'retract':
        #         pass
        #     if data['set'] == 'stop':
        #         pass
        if get_status:
            self.nw_client.publish(msg.topic, get_status)

    def __subscribe_task(self):
        while True:
            time.sleep(1)

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    nwmq = NWMQTT(config, port_config)
    # nwmq.connect()
    nwmq.start()