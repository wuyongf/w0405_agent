import time
import json
import paho.mqtt.client as mqtt
import os
import sys 
# yf
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
import src.models.transform as trans
import src.models.schema_rm as RMSchema

simPath = [
    {'x': 438, 'y': 398.0},  # P1
    {'x': 456.0, 'y': 364.0}, # P2
    {'x': 493.0, 'y': 382.0}, # P3
    {'x': 475.0, 'y': 419.0},  # P4
]

robotStatusJson = {
    "batteryPct": 100.0,
    "mapPose": {
        "mapId": "d7355d44-df67-4d26-8d25-36928746b7ee",
        "x": simPath[0]["x"],
        "y": simPath[0]["y"],
        "z": 0.0,
        "heading": 0.0
    },
    "state": 2
}

config = umethods.load_config('../../conf/config.properties')
rvapi = RVAPI.RVAPI(config)

robotStatus = json.dumps(robotStatusJson)

publisher = mqtt.Client("publisher_rm")
subscriber = mqtt.Client("subscriber_rm")


def publish_task_executing(task_id, task_type):
    task_status_json = {
        "taskId": task_id,
        "taskType": task_type,
        "taskStatusType": 1
    }
    task_status_msg = json.dumps(task_status_json)
    publisher.publish("/robot/task/status", task_status_msg)

def publish_task_complete(task_id, task_type):
    task_status_json = {
        "taskId": task_id,
        "taskType": task_type,
        "taskStatusType": 2
    }
    print("Publish Complete task...")
    task_status_msg = json.dumps(task_status_json)
    publisher.publish("/robot/task/status", task_status_msg)

def executeTask(task):
    global robotStatusJson
    task_json_object = json.loads(task)
    task = RMSchema.Task(json.loads(task))
    publish_task_executing(task.taskId, task.taskType)
    if  task_json_object["taskType"] == 'RM-LOCALIZE':
        # [x] retrieve map_id from robot-agent
        # [ ] retrieve rv_map_name from nwdb via map_ids
        # [ ] transform. pos_rm2rv. post init points.
        # [ ] rv: change to navigation status
        # [ ] rv: change map with init point.
        # [ ] rv: verify the active map. return status to rm
        print(task_json_object)
        pass
    if task_json_object["taskType"] == 'RM-GOTO':        
        robotStatusJson['mapPose']['mapId'] = task_json_object["parameters"]['mapId']
        robotStatusJson['mapPose']['x'] = task_json_object["parameters"]['x']
        robotStatusJson['mapPose']['y'] = task_json_object["parameters"]['y']
    if task_json_object["taskType"] == 'RV-LEDON':
        rvapi.set_led_status(on = 1)
    if task_json_object["taskType"] == 'RV-LEDOFF':
        rvapi.set_led_status(on = 0)
    if task_json_object["taskType"] == 'NW-BASIC-SLEEP1S':
        time.sleep(1)
    publish_task_complete(task_json_object["taskId"], task_json_object["taskType"])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    print("*******************************************************************************************************")
    print("message received ", str(msg.payload.decode("utf-8")))
    print("message topic=", msg.topic)
    print("*******************************************************************************************************")

    if msg.topic == '/rm/task':
        print("Exeucte Task...")        
        time.sleep(2)
        executeTask(str(msg.payload.decode("utf-8")))
        
if __name__ == "__main__":
    # abspath = os.path.abspath(sys.argv[0])
    # dname = os.path.dirname(abspath)
    # os.chdir(dname)

    publisher.connect("localhost")
    subscriber.connect("localhost")

    subscriber.on_message = on_message
    
    publisher.loop_start()
    subscriber.loop_start()

    while True:
        robotStatus = json.dumps(robotStatusJson)
        publisher.publish("/robot/status", robotStatus)
        subscriber.subscribe([("/robot/status", 0), ("/rm/task", 0), ("/robot/task/status", 0)])
        # subscriber.subscribe([("/robot/status", 0), ("/rm/task", 0), ("/robot/task/status", 0)])

        time.sleep(1)
