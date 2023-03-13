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

if __name__ == '__main__':
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    config = umethods.load_config('../../conf/config.properties')
    rvapi = RVAPI(config)
    res = rvapi.get_current_pose()
    print(res)