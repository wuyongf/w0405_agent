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
    
    def list_robot_skill(self):
        # http://dev.robotmanager.io/api/v2/robot-skills

        robotId = "2658a873-a0a6-4c3f-967f-d179c4073272"
        # robot-skills/get-by-robot/{robotId}
        data = self.get(f'/robot-skills/get-by-robot/{robotId}')

        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            print(f'skill: {item_name}  skill_id: {item_id}')
    
    def list_layouts(self):
        payload = {}
        payload["pageNo"] = 1
        payload["pageSize"] = 10
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]
        data = self.post('/layouts/list', json.dumps(payload))
        results = data['result']['list']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            print(f'layout: {item_name}  id: {item_id}')
    
    def list_layout_markers(self, layout_id):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        # layout_id = "ca0ac9aa-9910-4949-90d5-6efb525015b7"
        data = self.get(f'/layout-markers/{layout_id}')

        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            item_position = item['position']
            print(f'marker: {item_name}  id: {item_id} position: {item_position}')
        return results

    def create_layout_marker(self, layout_id, name):
        payload = {}
        payload["layoutId"] = layout_id
        payload["name"] = name
        payload["position"] = {"x": 20,"y": 20,"z": 0}
        return self.post('/layout-markers', json.dumps(payload))
        pass

    def delete_layout_marker(self, id):
        return self.delete(f'/layout-markers/{id}')
        pass
    
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
    
    def new_job(self):
        '''ref: https://docs.robotmanager.com/reference/create-a-mission'''
        payload = {}
        payload["type"] = 1 # 1: job 2: mission
        payload["mode"] = 1 # 1:Execute immediately
        payload["layoutId"] = 'ca0ac9aa-9910-4949-90d5-6efb525015b7'
        payload["name"] = 'Delivery'
        payload["robotIds"] = ['2658a873-a0a6-4c3f-967f-d179c4073272']
        payload['tasks'] = [
        {
            "skillId": "0ea62ced-e193-4452-b1d1-7955379371a7",
            "layoutId": "ca0ac9aa-9910-4949-90d5-6efb525015b7",
            "order": 1,
            "layoutMakerId": 1
        }]
        return self.post('/mission', json.dumps(payload))
    
    def delete_mission(self, mission_id):
        return self.delete(f'/mission/{mission_id}')
    
    ## for delivery
    def create_delivery_marker(self, layout_id, x, y, heading):
        
        delivery_names = []
        count = 0
        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            item_position = item['position']
            if "delivery" in item_name.lower():
                delivery_names.append(item_name)

        if len(delivery_names) == 0: count = 1
        else: 
            sorted_delivery_names = sorted(delivery_names)
            numeric_values = [int(item.split('-')[1]) for item in sorted_delivery_names]
            largest_number = max(numeric_values)
            count = largest_number+1

        payload = {}
        payload["layoutId"] = layout_id
        formatted_number = '{:02}'.format(count)
        payload["name"] = f'delivery-{formatted_number}'
        payload["position"] = {"x": x,"y": y,"z": heading}
        return self.post('/layout-markers', json.dumps(payload))

    def get_delivery_markers(self, layout_id):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            item_position = item['position']
            if "delivery" in item_name.lower():
                print(f'marker: {item_name}  id: {item_id} position: {item_position}')
        return results
    
    def get_latest_delivery_marker_guid(self, layout_id):
        delivery_markers = {}
        count = 0
        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            if "delivery" in item_name.lower():
                delivery_markers[item_name] = item_id

        if len(delivery_markers) == 0:
            print('cannot find any delivery marker!')
        else: 
            sorted_delivery_names = sorted(delivery_markers)
            numeric_values = [int(item.split('-')[1]) for item in sorted_delivery_names]
            largest_number = max(numeric_values)
            formatted_number = '{:02}'.format(largest_number)
            guid = delivery_markers[f'delivery-{formatted_number}']
            print(f'found latest delivery marker guid: {guid}')

    def delete_all_delivery_markers(self, layout_id):
        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            if "delivery" in item_name.lower():
                self.delete_layout_marker(item_id)

    
if __name__ == '__main__':
    config = load_config('./config.properties')
    rmapi = RMAPI(config)

    # json_data = rmapi.new_job()
    # print(json_data)
    
    # rmapi.list_robot_skill()
    # rmapi.list_layouts()

    # rmapi.create_layout_marker('ca0ac9aa-9910-4949-90d5-6efb525015b7', 'delivery-03')
    # rmapi.list_layout_markers('ca0ac9aa-9910-4949-90d5-6efb525015b7')
    # rmapi.delete_layout_marker()
    # rmapi.list_layout_markers()

    # delivery
    # rmapi.create_delivery_marker(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7', x=20, y=20, heading=0)
    # rmapi.delete_all_delivery_markers(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7')
    rmapi.get_delivery_markers(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7')
    # rmapi.get_latest_delivery_marker_guid(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7')

    # for delivery
    # 1. get sender name.   get sender location    (6/F... Point_A)
    # 2. get receiver name. get receiver location  (4/F... Point_C)

    # robot workflow:
    # move to 6/F Point_A. Maybe need to access door.
    # move to 6/F Lift Position. Call Lift.
    # enter lift.
    # switch to 4/F Map
    # move ot 4/F Point_C. 