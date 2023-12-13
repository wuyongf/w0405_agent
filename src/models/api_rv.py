import time
import logging, sys
import json
import uuid
# yf
import src.models.api_authenticated as api
import src.models.schema.rv as RVSchema
import src.utils.methods as umethods


class RVAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.base_url = config.get('RV', 'base_url')
        self.headers = {"X-API-Key": config.get('RV', 'X-API-Key'), "accept": "*/*", "Content-Type": "application/json"}
        super().__init__(base_url=self.base_url, headers=self.headers)

    def get_robot_id(self):
        return self.get_battery_state().robotId

    def get_battery_state(self):
        json_data = self.get('/battery/v1/state')
        return RVSchema.BatteryState(json_data)

    def set_led_status(self, on):
        if on:
            return self.put('/led/v1/ON')
        return self.put('/led/v1/OFF')

    # map
    def change_map(self, map_name):
        payload = {}
        payload["mapName"] = map_name
        payload["useInitialPose"] = False
        payload["waypointName"] = ''
        print(json.dumps(payload))
        return self.post('/map/v1/change', json.dumps(payload))

    def change_map2(self, map_name, positionName):
        payload = {}
        payload["mapName"] = map_name
        payload["useInitialPose"] = True
        payload["waypointName"] = positionName
        print(json.dumps(payload))
        return self.post('/map/v1/change', json.dumps(payload))

    def get_active_map(self):
        json_data = self.get(f'/map/v1/activeMap')
        if json_data is None: return json_data
        return RVSchema.ActiveMap(json_data)

    def get_active_map_json(self):
        return self.get(f'/map/v1/activeMap')

    def get_map_metadata(self, map_name):
        json_data = self.get(f'/map/v1/{map_name}/mapMetadata')
        # print(f'<debug> json_data: /map/v1/{map_name}/mapMetadata')
        if json_data is None: return json_data
        try:
            return RVSchema.MapMetadata(json_data)
        except:
            print(f'[RVAPI]: "get_map_metadata()" error')
            return None

    # mode
    def get_mode(self):
        json_data = self.get('/mode/v1')
        return RVSchema.Mode(json_data)

    def change_mode_navigation(self):
        return self.post('/mode/v1/navigation')

    def change_mode_undefined(self):
        return self.post('/mode/v1/undefined')

    def change_mode_followme(self, map_name=None):
        if map_name is None:
            return self.post('/mode/v1/followMe')
        return self.post('/mode/v1/followMe/{map_name}')

    # pose
    def get_current_pose(self):
        json_data = self.get('/localization/v1/pose')
        # logging.debug(json)
        return RVSchema.Pose(json_data)

    def update_initial_pose(self, x, y, angle):
        payload = {}
        payload["x"] = x
        payload["y"] = y
        payload["angle"] = angle
        print(json.dumps(payload))
        return self.put('/localization/v1/initialPose', json.dumps(payload))

    def check_current_pose_valid(self):
        json_data = self.get('/localization/v1/pose/deviation')
        return json_data['poseValid']

    # waypoint
    def post_new_waypoint(self, map_name, pose_name, x, y, angle):
        payload = {}
        payload["id"] = 0
        payload["name"] = pose_name
        payload["mapName"] = map_name
        payload["x"] = x
        payload["y"] = y
        payload["angle"] = angle
        print(json.dumps(payload))
        return self.post('/waypoint/v1', json.dumps(payload))

    def list_waypoints(self, map_name):
        pass

    def delete_all_waypoints(self, map_name):
        # /waypoint/v1?mapName=5W516_20230313&waypointId=-1&initialLocalization=false
        return self.delete(f'/waypoint/v1?mapName={map_name}&waypointId=-1&initialLocalization=false')

    # navigation
    def post_navigation_pose(self, x, y, angle):
        payload = {}
        payload["x"] = x
        payload["y"] = y
        payload["angle"] = angle
        print(json.dumps(payload))
        return self.post('/navigation/v1/pose', json.dumps(payload))

    def get_navigation_result(self):
        json_data = self.get('/navigation/v1/result')
        if json_data is None: return json_data
        return json_data["goalStatus"]["status"]

    # task
    def delete_current_task(self):
        return self.delete('/task/v1/move')

    def post_new_navigation_task(self, waypoint_name, orientationIgnored):
        movement_payload = {}
        actionList = {}
        taskItemList_payload = {}
        payload = {}

        movement_payload['waypointName'] = waypoint_name
        movement_payload['navigationMode'] = 'AUTONOMY'
        movement_payload['orientationIgnored'] = orientationIgnored

        actionList['alias'] = 'NIL'

        taskItemList_payload['actionList'] = [actionList]
        taskItemList_payload['movement'] = movement_payload

        payload["taskId"] = str(uuid.uuid1())
        payload["taskItemList"] = [taskItemList_payload]
        data = json.dumps(payload)
        print(f'[post_new_navigation_task]: {data}')
        return self.post('/task/v1/move', json.dumps(payload))

    def get_task_is_completed(self):
        json_data = self.get('/task/v1/status')
        if json_data is None: return json_data
        if (json_data["taskCompletionDTO"] is None): return False
        return json_data["taskCompletionDTO"]["completed"]

    def get_task_is_cancelled(self):
        json_data = self.get('/task/v1/status')
        if json_data is None: return json_data
        if (json_data["taskCompletionDTO"] is None): return False
        return json_data["taskCompletionDTO"]["cancelled"]

    def get_task_has_exception(self):
        json_data = self.get('/task/v1/status')
        if json_data is None: return json_data
        if (json_data["taskCompletionDTO"] is None): return False
        return json_data["taskCompletionDTO"]["exception"]

    # baseControl
    def get_robot_is_moving(self):
        json_data = self.get('/baseControl/v1/move')
        # json_data = self.get('/task/v1/status')
        if json_data is None: return json_data
        return json_data["moving"]

    def pause_robot_task(self):
        return self.put('/baseControl/v1/pause')

    def resume_robot_task(self):
        return self.put('/baseControl/v1/resume')

    def switch_manual(self, on=False):
        if (on): return self.put('/baseControl/v1/manual/ON')
        else: return self.put('/baseControl/v1/manual/OFF')

    # Docking
    def post_charging(self, upperLimit, duration_min, shutdownAfterCharging=False):
        """
        upperLimit: 0-100
        """
        payload = {}
        payload["upperLimit"] = upperLimit
        payload["duration"] = duration_min
        payload["shutdownAfterCharging"] = shutdownAfterCharging
        print(json.dumps(payload))
        return self.post('/docking/v1/charging', json.dumps(payload))

    def delete_charging(self):
        return self.delete(f'/docking/v1/charging')

    def get_charging_feedback(self):
        json_data = self.get('/docking/v1/charging/feedback')
        # json_data = self.get('/task/v1/status')
        if json_data is None: return json_data
        return json_data["chargingStatus"]

    def get_followme_pairing_state(self):
        json_data = self.get('/followMe/v1/pairing')
        if json_data is None: return json_data
        return json_data["pairingState"]

    def post_followme_pair(self):
        return self.post('/followMe/v1/pairing/pair')

    def post_followme_unpair(self):
        return self.post('/followMe/v1/pairing/unpair')
    
    # Safety Zone
    def put_safety_zone_minimum(self):
        return self.put('/baseControl/v1/safetyZone/MINIMUM')
    
    # Maximun Speed
    def put_maximum_speed(self, max_speed):
        return self.put(f'/baseControl/v1/speed/{max_speed}')
    
    # Check Boot Up Successful
    def wait_for_ready(self):
        
        while(True):
            print(f'check robot is ready or not....')
            time.sleep(1)

            json_data = self.get('/battery/v1/state')
            if json_data is not None: 
                break
            else:
                continue
        
        print(f'robot is ready!!!')
        return True
    
    # status-mode
    def get_status_estop(self):
        json_data = self.get('/baseControl/v1/estop')
        if json_data is None: return json_data
        return json_data["stopped"]


if __name__ == '__main__':
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    config = umethods.load_config('../../conf/config.properties')
    rvapi = RVAPI(config)

    res = rvapi.get_status_estop()
    print(res)

    ####################################################################################################
    # Robot
    ####################################################################################################
    # rvapi.check_is_ready()

    ####################################################################################################
    # Charging
    ####################################################################################################
    # res = rvapi.get_charging_feedback()
    # print(res)
    # rvapi.post_charging(upperLimit=100,duration_min=60,shutdownAfterCharging=False)
    # rvapi.delete_charging()

    # res = rvapi.post_new_navigation_task('11',orientationIgnored=True)

    ####################################################################################################
    # Get Robot Status - is moving or not
    ####################################################################################################
    # while(True):
    #     time.sleep(1)
    #     res = rvapi.get_robot_is_moving()
    #     print(res)

    ####################################################################################################
    # # # post 2 predefined position
    # rvapi.post_new_waypoint('5W516_20230313','WAYPOINT1', -0.0226, 0.00776, 0.7872831189896021)
    # rvapi.post_new_waypoint('5W516_20230313','WAYPOINT2', 0.37553, 0.39732, 0.7161085920932735)

    # # delete all points
    # rvapi.delete_all_waypoints('5W516_20230313')
    ####################################################################################################

    # # print(rvapi.get_battery_state().percentage)
    # res = rvapi.get_active_map()
    # print(res.name)

    # rvapi.change_mode_navigation()
    # res = rvapi.get_mode()
    # print(res.state)

    # rvapi.change_map2('5W_20230308_2', 'WP01')
    # rvapi.change_map2('5W516-20230424', 'CHARGING')
    # res = rvapi.get_active_map()
    # print(res.name)

    ###################
    # 2 points: p1 = (-0.037, 0.0150, 0.785) p2 = (0.412, 0.484, 0.784)

    ####################################################################################################
    # Follow Me Workflow
    ####################################################################################################

    # # rvapi.change_mode_navigation()
    # # time.sleep(5)
    # # rvapi.change_mode_followme()
    # # time.sleep(5)
    # # rvapi.post_followme_pair()
    # # time.sleep(5)
    # while True:
    #     res = rvapi.get_followme_pairing_state()
    #     print(res)
    #     time.sleep(1)

    # # rvapi.post_followme_unpair()
