import api_authenticated as api
import schema_rv
import useful_functions.methods as um
import logging, sys

class RVAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.config = config
        self.base_url = self.config.get('RV','base_url')
        self.headers = {"X-API-Key": self.config.get('RV','X-API-Key')}
        super().__init__(base_url=self.base_url, headers=self.headers)

    def getBatteryState(self):
        json = self.get('/battery/v1/state')
        return schema_rv.BatteryState(json)
    
    def getCurrentPostion(self):
        json = self.get('/localization/v1/pose')
        # logging.debug(json)
        return schema_rv.Pose(json)

if __name__ == '__main__':
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    config = um.load_config('../../conf/config.properties')
    rvapi = RVAPI(config)
    res = rvapi.getBatteryState()
    print(res.percentage)