import time
import threading
import paho.mqtt.client as mqtt
import json
#yf
import src.utils.methods as umethods
import src.models.schema_rv as RVSchema
class RVMQTT():
    def __init__(self, config):
        localhost = config.get('RV','localhost')
        # self.mq_publisher = mqtt.Client("rv_mqtt_publisher")
        self.mq_subscriber = mqtt.Client("rv_mqtt_subscriber")
        self.mq_subscriber.connect(localhost)
        self.mq_subscriber.on_message = self.__on_message

        # init
        self.a = RVSchema.Pose
        self.rv_x = self.rv_y = self.rv_angle = 0.0

    def start(self):
        self.mq_subscriber.loop_start()
        threading.Thread(target=self.__subscribe_task).start()   # from RV API
        print('[RVMQTT] Start...')

    def __on_message(self, client, userdata, msg):
        # # print(msg.topic+" "+str(msg.payload))
        print("*******************************************************************************************************")
        print("message received ", str(msg.payload.decode("utf-8")))
        print("message topic=", msg.topic)
        print("*******************************************************************************************************")
        self.__parse_message(msg)

    def __parse_message(self, msg):
        topic = msg.topic
        data = json.loads(str(msg.payload.decode("utf-8")))
        if topic == 'rvautotech/fobo/pose':
            self.rv_x = data['x']
            self.rv_y = data['y']
            self.rv_angle = data['angle']

    def __subscribe_task(self):
        while True:
            # publisher.publish("/robot/status", robotStatus)
            topic = 'rvautotech/fobo/pose'
            self.mq_subscriber.subscribe(topic, 2)
            # self.mq_subscriber.subscribe(self.mq_subs_topic, 2)
            time.sleep(1)
    
    def get_current_pose(self):
        return self.rv_x, self.rv_y, self.rv_angle

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    
    rvmqtt = RVMQTT(config)

    rvmqtt.start()

    while(True):
        print(rvmqtt.get_current_pose())
        time.sleep(1)
        