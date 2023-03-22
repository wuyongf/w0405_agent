import logging, sys
import json
# yf
import src.models.api_authenticated as api
import src.models.schema_rv as RVSchema
import src.utils.methods as umethods


class RVAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.base_url = config.get('RV','base_url')
        self.headers = {
            "X-API-Key": config.get('RV','X-API-Key'),
            "accept":  "*/*",
            "Content-Type": "application/json"}
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
        return RVSchema.MapMetadata(json_data)
    
    # mode
    def get_mode(self):
        json_data = self.get('/mode/v1')
        return RVSchema.Mode(json_data)
        
    def change_mode_navigation(self):
        return self.post('/mode/v1/navigation')
    
    def change_mode_undefined(self):
        return self.post('/mode/v1/undefined')
    
    def change_mode_followme(self, map_name = None):
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
    def post_new_waypoint(self, map_name, pose_name,  x, y, angle):
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
    
    # base control
    def check_is_moving(self):
        json_data = self.get('/baseControl/v1/move')
        return json_data['moving']

if __name__ == '__main__':
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    config = umethods.load_config('../../conf/config.properties')
    rvapi = RVAPI(config)

    res = rvapi.post_navigation_pose(0.3076,0.295,0)
    print(res)
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

    # # # rvapi.change_map('5W_20230308_2', 'WP01') 
    # rvapi.change_map('5W516_20230313', 'WAYPOINT1')
    # res = rvapi.get_active_map()
    # print(res.name)


    ###################
    # 2 points: p1 = (-0.037, 0.0150, 0.785) p2 = (0.412, 0.484, 0.784)

    

    ###################
