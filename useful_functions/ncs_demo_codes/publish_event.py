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
            "title": "Example Event",
            "description": "Example of how to send event to Robot Agent",
            "metadata": {
                "name": "John",
                "match": 80,
                "gender": "Male",
                "ageGroup": "Young",
                "glasses": "Yes"
            },
            "severity": 1,
            "medias": [{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/front_left.png",
                "type": 1,
                "title": "Front Left",
                "360View": False
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/front_right.png",
                "type": 1,
                "title": "Front Right",
                "360View": False
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/front.png",
                "type": 1,
                "title": "Front",
                "360View": False
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/main_cam.png",
                "type": 1,
                "title": "Main",
                "360View": False
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/paranomic.png",
                "type": 1,
                "360View": True 
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/rear_left.png",
                "type": 1,
                "title": "Rear Left",
                "360View": False
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/rear_right.png",
                "type": 1,
                "title": "Rear Right",
                "360View": False
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/rear.png",
                "type": 1,
                "title": "Rear",
                "360View": False
            },{
                "filePath": "C:/dev/w0405_agent/useful_functions/ncs_demo_codes/event_images/poi.png",
                "type": 1,
                "title": "POI details"
            }],
            "mapPose" : {
                "mapId": map_id,
                "x": x,
                "y": y,
                "z": z,
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
