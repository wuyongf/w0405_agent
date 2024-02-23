import time
import threading
import paho.mqtt.client as mqtt
import json
#yf
import src.utils.methods as umethods
import src.models.schema.rv as RVSchema
class RVMQTT():
    def __init__(self, config):
        self.broker_address = config.get('RV','localhost')
        # print(self.broker_address)
        self.subscriber = mqtt.Client("rv_mqtt_subscriber")
        self.subscriber.connect(self.broker_address)
        self.subscriber.on_message = self.__on_message

        topics = []
        topics.append(['rvautotech/fobo/pose',2])
        topics.append(['rvautotech/fobo/battery',2])
        topics.append(['rvautotech/fobo/map/active',2])
        topics.append(['rvautotech/fobo/baseController/move',2])
        self.subscriber.subscribe(topics)

        self.subscriber.loop_start()

        # init-mqtt
        self.connected = False
        # init-pos
        self.robotId = self.mapName = None
        self.x = self.y = self.angle = 0.0
        # init-battery
        self.percentage = 0.0
        self.powerSupplyStatus = None
        # init-map
        self.resolution = 0.05
        self.originX = self.originY = 0.0
        self.imageWidth = self.imageHeight = 0
        # init-mission/task
        self.moving = True
        self.task_is_executing = False

    def start(self):
        
        threading.Thread(target=self.__subscribe_task).start()   # from RV API
        print('[RVMQTT] Start...')

    def __on_message(self, client, userdata, msg):
        # # print(msg.topic+" "+str(msg.payload))
        # print("*******************************************************************************************************")
        # print("message received ", str(msg.payload.decode("utf-8")))
        # print("message topic=", msg.topic)
        # print("*******************************************************************************************************")
        self.__parse_message(msg)

    def __parse_message(self, msg):
        topic = msg.topic
        data = json.loads(str(msg.payload.decode("utf-8")))
        if topic == 'rvautotech/fobo/pose':
            self.robotId = data['robotId']
            self.mapName = data['mapName']
            self.x = data['x']
            self.y = data['y']
            self.angle = data['angle']
        if topic == 'rvautotech/fobo/battery':
            self.percentage = data['percentage']
            self.powerSupplyStatus = data['powerSupplyStatus']
        if topic == 'rvautotech/fobo/baseController/move':
            self.moving = data['moving']
            pass
        if topic == 'rvautotech/fobo/map/active':
            pass
            # self.resolution = data['resolution']
            # self.originX = data['originX']
            # self.originY = data['originY']
            # self.imageWidth = data['imageWidth']
            # self.imageHeight = data['imageHeight']

    def __subscribe_task(self):
        while True:
            time.sleep(0.1)
    
    ## Get Methods
    def get_powerSupplyStatus(self):
        return self.powerSupplyStatus

    def get_battery_percentage(self):
        return self.percentage
    
    def get_current_map_name(self):
        return self.mapName
    
    def get_current_pose(self):
        return self.x, self.y, self.angle
    
    def get_robot_is_moving(self):
        return self.moving

import src.models.trans as Trans

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')

    T = Trans.RVRMTransform()

    rvmqtt = RVMQTT(config)

    rvmqtt.start()


    while(True):
        pos = rvmqtt.get_current_pose()
        print(pos)
        
        time.sleep(0.1)
    
