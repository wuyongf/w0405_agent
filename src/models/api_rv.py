import src.models.api_authenticated as api
import src.models.schema_rv as RVSchema
import src.utils.methods as umethods
import logging, sys

class RVAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.base_url = config.get('RV','base_url')
        self.headers = {"X-API-Key": config.get('RV','X-API-Key')}
        super().__init__(base_url=self.base_url, headers=self.headers)

    def get_battery_state(self):
        json = self.get('/battery/v1/state')
        return RVSchema.BatteryState(json)
    
    def get_current_pose(self):
        json = self.get('/localization/v1/pose')
        # logging.debug(json)
        return RVSchema.Pose(json)
    
    def set_led_status(self, on):
        if on:
            return self.put('/led/v1/ON')
        return self.put('/led/v1/OFF')
    
    def get_map_metadata(self, map_name):
        json = self.get(f'/map/v1/{map_name}/mapMetadata')
        return RVSchema.MapMetadata(json)
    
    def get_mode(self):
        json = self.get('/mode/v1')
        return RVSchema.Mode(json)
        
    def change_mode_navigation(self):
        return self.post('/mode/v1/navigation')
    
    def change_mode_undefined(self):
        return self.post('/mode/v1/undefined')

if __name__ == '__main__':
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    config = umethods.load_config('../../conf/config.properties')
    rvapi = RVAPI(config)
    
    res = rvapi.change_mode_navigation()
    print(res)