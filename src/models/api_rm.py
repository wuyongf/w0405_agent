import src.models.api_authenticated as api
import json
import requests
import src.utils.methods as umethods
import sys

class RMAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.config = config
        self.base_url = self.config.get('RM','base_url')
        self.headers = {
            "Authorization": self.__login(),
            "Content-Type": "application/json"
            }
        super().__init__(base_url=self.base_url, headers=self.headers)

    # def thread_login(self):
    #     continue_flag = True
    #     while(continue_flag):
    #         try:
    #             self.token = self.login()
    #             continue_flag = False
    #         except:
    #             print('[api_rm] login failed, retry...')
    
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
        payload = {}
        payload["type"] = 1
        payload["mode"] = 1
        payload["layoutId"] = 'd3b4f645-023d-45e8-95df-3ef6465497e9'
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
    
    def get_mission_id(self, task_json):
        # self.__init__()
        json_data = self.list_missions()
        # print(json_data)
        if json_data is not None:
            list_data = json_data['result']['list']
            # print(list_data)
            for mission in list_data:
                # taskId == mission['tasks']['id']
                if mission['tasks'] is None: continue
                else:
                    for task in mission['tasks']:
                        if (task_json['taskId'] == task['id']):
                            return mission['id']
        else: 
            print('[api_rm.get_mission_id]: cannot find the mission_id')
            return None

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    rmapi = RMAPI(config)

    # json_data = rmapi.create_mission()
    # print(json_data)

    # ## list map
    # json_data = rmapi.list_maps()
    # print(json_data)

    # taskId = '732411b8-dded-40b0-a8d3-ca501bd21267'

    # list missions and parse json
    json_data = rmapi.list_missions()

    print(json_data)
    # # print(json_data)
    # list_data = json_data['result']['list']
    # # print(list_data)
    # # print(len(list_data))
    # for mission in list_data:
    #     # taskId == mission['tasks']['id']
    #     if mission['tasks'] is None: continue
    #     else:
    #         for task in mission['tasks']:
    #             if (taskId == task['id']):
    #                 print('found!')
    #                 print('mission_id: ',  mission['id'])
    #                 break

    # # # get mission status
    # # for i in range(len(list_data)):
    # #     print(list_data[i]['status'])
    
    # # # get Mission(Job or Mission)
    # # for i in range(len(list_data)):
    # #     if(list_data[i]['type'] == 2):
    # #         print(list_data[i])

