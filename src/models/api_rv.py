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

    def get_battery_state(self):
        json_data = self.get('/battery/v1/state')
        return RVSchema.BatteryState(json_data)
    
    def get_current_pose(self):
        json_data = self.get('/localization/v1/pose')
        # logging.debug(json)
        return RVSchema.Pose(json_data)
    
    def set_led_status(self, on):
        if on:
            return self.put('/led/v1/ON')
        return self.put('/led/v1/OFF')
    
    def change_map(self, map_name, point_name):
        payload = {}
        payload["mapName"] = map_name
        payload["useInitialPose"] = True
        payload["waypointName"] = point_name
        print(json.dumps(payload))
        return self.post('/map/v1/change', json.dumps(payload))

    def get_active_map(self):
        json_data = self.get(f'/map/v1/activeMap')
        return RVSchema.ActiveMap(json_data)

    def get_map_metadata(self, map_name):
        json_data = self.get(f'/map/v1/{map_name}/mapMetadata')
        return RVSchema.MapMetadata(json_data)
    
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


if __name__ == '__main__':
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    config = umethods.load_config('../../conf/config.properties')
    rvapi = RVAPI(config)

    print(rvapi.get_battery_state().percentage)
    # res = rvapi.get_active_map()
    # print(res.name)

    # rvapi.change_mode_navigation()
    # res = rvapi.get_mode()
    # print(res.state)

    # rvapi.change_map('5W516_20230313', 'WAYPOINT1') # 5W_20230308_2 WP01    5W516_20230313 WAYPOINT1
    # res = rvapi.get_active_map()
    # print(res.name)


    