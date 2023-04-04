import api_authenticated as api
import json
import requests
import sys
import configparser

def load_config(config_addr):
        # Load config file
        configs = configparser.ConfigParser()
        try:
            configs.read(config_addr)
        except:
            print("Error loading properties file, check the correct directory")
        return configs

class RMAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.config = config
        self.base_url = self.config.get('RM','base_url')
        self.headers = {
            "Authorization": self.__login(),
            "Content-Type": "application/json"
            }
        super().__init__(base_url=self.base_url, headers=self.headers)


    def __login(self):
        base_url = self.base_url
        endpoint = "/login"
        payload = {}
        payload["username"] = self.config.get('RM','username')
        payload["password"] = self.config.get('RM','password')
        payload["companyId"] = self.config.get('RM','companyId')

        headers = {"Content-Type":"application/json"}
        response = requests.post(url=base_url + endpoint, headers=headers, data=json.dumps(payload))
        return json.loads(response.text)["token"]

    def get_login_info(self):
        return self.get('/auth/loginInfo')
    
    def list_layouts(self):
        payload = {}
        payload["pageNo"] = 1
        payload["pageSize"] = 10
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]
        return self.post('/layouts/list', json.dumps(payload))
    
    def list_maps(self):
        payload = {}
        payload["pageNo"] = 1
        payload["pageSize"] = 10
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]
        return self.post('/map/list', json.dumps(payload))
    
    def list_missions(self):
        payload = {}
        payload["pageNo"] = sys.maxsize
        payload["pageSize"] = sys.maxsize
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]
        return self.post('/mission/list', json.dumps(payload))
    
    def create_mission(self):
        '''ref: https://docs.robotmanager.com/reference/create-a-mission'''
        payload = {}
        payload["type"] = 1
        payload["mode"] = 1
        payload["layoutId"] = 'd3b4f645-023d-45e8-95df-3ef6465497e6'
        payload["name"] = 'TestMission-Rev03'
        payload["robotIds"] = ['2658a873-a0a6-4c3f-967f-d179c4073272']
        payload['tasks'] = [
        {
            "skillId": "f8919eca-c5f2-4b33-8efd-d2222107cfba",
            "layoutId": "d3b4f645-023d-45e8-95df-3ef6465497e6",
            "order": 1,
            "layoutMakerId": 1
        }]
        return self.post('/mission', json.dumps(payload))
    
    def delete_mission(self, mission_id):
        return self.delete(f'/mission/{mission_id}')

if __name__ == '__main__':
    config = load_config('./config.properties')
    rmapi = RMAPI(config)

    json_data = rmapi.create_mission()
    print(json_data)
