import paho.mqtt.client as mqtt
import json
import time

# Set MQTT broker IP address and port number
broker_address = "192.168.1.56"
broker_port = 1883

# Define topic and payload
topic = "rvautotech/fobo/joystick"
payload = {
    "className": "com.rvautotech.fobo.amr.dto.JoystickDTO",
    "object": 
    {
        "upDown": 0.5,
        "leftRight": 0,
        "turboOn": False
    }
}

# Convert payload to JSON string
payload_str = json.dumps(payload)

# Create MQTT client and connect to broker
client = mqtt.Client()
client.connect(broker_address, broker_port)

# Publish message
while(True):
    client.publish(topic, payload_str)
    time.sleep(0.01)
    print('1')


# Disconnect from broker
client.disconnect()