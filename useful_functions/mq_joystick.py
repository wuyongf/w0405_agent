import paho.mqtt.client as mqtt
import json
import time


if __name__ == "__main__":

    # Set MQTT broker IP address and port number
    broker_address = "192.168.1.56"
    broker_port = 1883

    # Define topic and payload
    topic = "rvautotech/fobo/joystick"
    payload = {
            "upDown": 0,
            "leftRight": 0,
            "turboOn": False
        }

    # Convert payload to JSON string
    payload_str = json.dumps(payload)

    # Create MQTT client and connect to broker
    client = mqtt.Client('joystick_publisher')
    client.connect(broker_address, broker_port)
    client.loop_start()

    # Publish message
    while(True):
        client.publish(topic, payload_str)
        time.sleep(0.01)
        print('1')


    # Disconnect from broker
    client.disconnect()