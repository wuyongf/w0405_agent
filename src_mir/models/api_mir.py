import time
import logging, sys
import json
import uuid
# yf
import src.models.api_authenticated as api
import src.models.schema.rv as RVSchema
import src_mir.models.shcema.mir as MiRSchema
import src.utils.methods as umethods

class MiRAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.base_url = config.get('MiR', 'base_url')
        self.headers = {"Authorization": 'Basic ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA==', 
                        "Accept-Language": "en_US", 
                        "Content-Type": "application/json", 
                        "accept": "application/json"}
        super().__init__(base_url=self.base_url, headers=self.headers)

    def get_status(self):
        json_data = self.get('/status')
        return MiRSchema.Status(json_data)
    
    def play(self):

        # print(config.get('MiR', 'Authorization'))
        payload = {}
        payload["state_id"] = 3
        print(json.dumps(payload))
        return self.put('/status', json.dumps(payload))
    
    def post_rmove_mission(self):
        payload = {}
        payload["mission_id"] = '9b36e001-bb32-11ee-b5ac-00012978eb45'
        print(json.dumps(payload))
        return self.post('/mission_queue', json.dumps(payload))

    def rmove_demo(self):
        self.post_rmove_mission()
        time.sleep(2)
        self.play()
        return True

if __name__ == '__main__':

    config = umethods.load_config('../../conf/config_mir.properties')
    mirapi = MiRAPI(config)

    # res = mirapi.get_status()
    # print(res.percentage)

    res = mirapi.rmove_demo()
