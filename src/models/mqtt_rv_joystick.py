import paho.mqtt.client as mqtt
import json
import time
# yf
import src.utils.methods as umethods
import src.models.api_rv as RVAPI

# workflow:
# 1. switch to manual mode
# 2. publish mqtt topic

class RVJoyStick():
    def __init__(self, config):
        # Init1: Create MQTT client and connect to broker
        self.broker_address = config.get('RV','localhost')
        self.client = mqtt.Client('rv_joystick_publisher')
        self.client.connect(self.broker_address, port=1883)
        self.client.loop_start()
        self.rvapi = RVAPI.RVAPI(config)

    def enable(self):
        '''to enable the joystick. switch on AMR manual mode'''
        return self.rvapi.switch_manual(True)

    def disable(self):
        ''' to disable the joystick. switch off AMR manual mode'''
        return self.rvapi.switch_manual(False)
    
    def stop(self):
        ''' to stop the AMR'''
        return self.move(0,0)
    
    def move(self, upDown = 0, leftRight = 0, turboOn = False):
        ''' to move the AMR. variables range: [-1,1] '''
        # Define topic and payload
        topic = "rvautotech/fobo/joystick"
        payload = {
            "upDown": upDown,
            "leftRight": leftRight,
            "turboOn": turboOn
            }
        # Convert payload to JSON string
        payload_str = json.dumps(payload)
        # Publish message
        self.client.publish(topic, payload_str)

if __name__ == "__main__":

    config = umethods.load_config('../../conf/config.properties')

    joystick = RVJoyStick(config)

    print('enable the joystick...')
    joystick.enable()
    time.sleep(2)
    joystick.disable()

    # count = 0
    # while(True):
    #     joystick.move()
    #     time.sleep(0.02)
    #     print('count = ',count)
    #     count += 1
    #     if(count > 200): break
    # joystick.stop()

    # print('disable the joystick...')
    # time.sleep(2)
    # joystick.disable()