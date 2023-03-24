import time
import json
import paho.mqtt.client as mqtt
import os
import sys 
# yf
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
import src.models.trans_rvrm as Trans
import src.models.schema_rm as RMSchema
import src.models.db_robot as RobotDB

config = umethods.load_config('../../conf/config.properties')
rvapi = RVAPI.RVAPI(config)
nwdb = RobotDB.robotDBHandler(config)
trans = Trans.RVRMTransform()

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

def publish_task_failed(task_id, task_type):
    task_status_json = {
        "taskId": task_id,
        "taskType": task_type,
        "taskStatusType": 3
    }
    print("task failed...")
    task_status_msg = json.dumps(task_status_json)
    publisher.publish("/robot/task/status", task_status_msg)

def execute_task(task):
    global robotStatusJson
    task_json_object = json.loads(task)
    task = RMSchema.Task(json.loads(task))
    publish_task_executing(task.taskId, task.taskType)
    if task.taskType == 'RM-LOCALIZE':
        try:
            # step 1. get rm_map_id, rv_map_name, map_metadata
            rm_map_metadata = task.parameters # from robot-agent
            rv_map_name = nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = rvapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            trans.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x, rv_map_metadata.y, rv_map_metadata.angle)
            rv_waypoint = trans.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x, rm_map_metadata.y, rm_map_metadata.heading)
            # step 3. rv. create point base on rm. localization.
            rvapi.delete_all_waypoints(rv_map_name)
            rvapi.post_new_waypoint(rv_waypoint.mapName, rv_waypoint.name, rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            rvapi.change_mode_navigation()
            rvapi.change_map(rv_map_name)
            rvapi.update_initial_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            # step 4. double check
            pose_is_valid = 1#rvapi.check_current_pose_valid()
            map_is_active = rvapi.get_active_map().name == rv_map_name
            if(pose_is_valid & map_is_active):
                publish_task_complete(task.taskId, task.taskType)
            else:
                print('[RM-LOCALIZE] Error: Please check robot position is the same as the point on map.')
                publish_task_failed(task.taskId, task.taskType)
        except:
            print('[RM-LOCALIZE] Error: Please check the workflow.')
            publish_task_failed(task.taskId, task.taskType)
        
    if task.taskType == 'RM-GOTO':
        try:
            # step 1. get rm_map_id, rv_map_name, map_metadata
            rm_map_metadata = task.parameters # from robot-agent
            rv_map_name = nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = rvapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            trans.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x, rv_map_metadata.y, rv_map_metadata.angle)
            rv_waypoint = trans.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x, rm_map_metadata.y, rm_map_metadata.heading)
            # step3. rv. create point base on rm. localization.
            rvapi.post_navigation_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            # check if it has arrived
            while(rvapi.get_navigation_result() is None): time.sleep(1)
           
            # step 4. double check
            navigation_is_succeeded = rvapi.get_navigation_result()['status'] == 'SUCCEEDED'
            pose_is_valid = rvapi.check_current_pose_valid()
            map_is_active = rvapi.get_active_map().name == rv_map_name
            if(navigation_is_succeeded & pose_is_valid & map_is_active):
                publish_task_complete(task.taskId, task.taskType)
            else:
                print('[RM-GOTO] Error: Please check robot position is the same as the point on map.')
                publish_task_failed(task.taskId, task.taskType)
        except:
            print('[RM-GOTO] Error: Please check the workflow.')
            publish_task_failed(task.taskId, task.taskType)

        # # robot position        
        # robotStatusJson['mapPose']['mapId'] = task_json_object["parameters"]['mapId']
        # robotStatusJson['mapPose']['x'] = task_json_object["parameters"]['x']
        # robotStatusJson['mapPose']['y'] = task_json_object["parameters"]['y']
    
    if task.taskType == 'RV-LEDON':
        rvapi.set_led_status(on = 1)
    
    if task.taskType == 'RV-LEDOFF':
        rvapi.set_led_status(on = 0)
    
    if task.taskType == 'NW-BASIC-SLEEP1S':
        time.sleep(1)

    publish_task_complete(task.taskId, task.taskType)

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
        execute_task(str(msg.payload.decode("utf-8")))
        
if __name__ == "__main__":

    publisher.connect("localhost")
    subscriber.connect("localhost")

    subscriber.on_message = on_message
    
    publisher.loop_start()
    subscriber.loop_start()

    while True:

        # publisher.publish("/robot/status", robotStatus)
        subscriber.subscribe([("/robot/status", 0), ("/rm/task", 0), ("/robot/task/status", 0)])
        time.sleep(1)
