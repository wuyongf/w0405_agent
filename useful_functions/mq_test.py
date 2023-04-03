import paho.mqtt.client as mqtt

# Set up MQTT client
client = mqtt.Client()
client.connect("localhost")

# Publish message to topic
topic = "mytopic"
message = "Hello, world!"
client.publish(topic, message)

# Disconnect from broker
client.disconnect()