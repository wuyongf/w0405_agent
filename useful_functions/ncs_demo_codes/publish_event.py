#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Goh Kae Yan, NCS Product and Platforms, RobotManager
# Created Date: 20 Dec 2022
# version ='1.0'
# ---------------------------------------------------------------------------
"""Example client code to publish event to Robot Agent v2.0"""  
# ---------------------------------------------------------------------------
import time
import json
import paho.mqtt.client as mqtt
import logging
import uuid

logging.basicConfig(format='%(asctime)s - line:%(lineno)d - %(levelname)s - %(message)s',level=logging.DEBUG)

"""  Config for MQTT connection """  
client_name = 'Event Publisher'
mqtt_host = 'localhost'
mqtt_port = 1883
event_topic = '/robot/event' 
qos = 2   
client = mqtt.Client(client_name)

if __name__ == "__main__":
    try: 
        logging.info("Connecting to MQTT: %s %d", mqtt_host, mqtt_port)
        client.connect(host=mqtt_host, port=mqtt_port)
        client.loop_start()

        """ Event parameters """ 
        map_id = "56ded5f9-79a3-458e-8458-8a76e818048e"  # Replace it with actual value   
        x = 1.0
        y = 1.0
        z = 1.0
        heading = 360

        event_json = {
            "eventId": str(uuid.uuid1()), 
            "title": "Example Event1",
            "description": "Example of how to send event to Robot Agent",
            "metadata": {},
            "severity": 1,
            "medias": [{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/front_left.png",
                "type": 1,
                "title": "Front Left",
                "360View": False
            }],
            "mapPose" : {
                "mapId": map_id,
                "x": x,
                "y": y,
                "heading": heading
            }
        }

        """  Publish the event to robot agent """ 
        if map_id == "": 
            logging.fatal('Unable to run the script')
            logging.fatal('Please replace map_id with actual value')
        else: 
            event = json.dumps(event_json)
            logging.info("Publish Event Message, topic: {}, msg: {}".format(event_topic, event_json))
            client.publish(event_topic, event)   
            time.sleep(2)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: ending MQTT client")
        client.loop_stop()
        client.disconnect()


# {"eventId": "a6bb5565-cfa9-11ed-af92-2c8db1a964f5", "title": "event_test_rev01", "description": "This is an event test", "metadata": {}, "severity": 1, "medias": "[{\"filePath\": \"C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/front_right.png\", \"type\": 1, \"title\": \"Front Right\", \"360view\": false}]", "mapPose": "{\"mapId\": \"e672cbec-9bd5-4e57-baeb-091784003481\", \"x\": 54.0, \"y\": 60.0, \"heading\": 90.0}"}
# {'eventId': '66fe33df-cfaa-11ed-9820-2c8db1a964f5', 'title': 'Example Event1', 'description': 'Example of how to send event to Robot Agent', 'metadata': {}, 'severity': 1, 'medias': [{'filePath': 'C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/front_left.png', 'type': 1, 'title': 'Front Left', '360View': False}], 'mapPose': {'mapId': '56ded5f9-79a3-458e-8458-8a76e818048e', 'x': 1.0, 'y': 1.0, 'heading': 360}}