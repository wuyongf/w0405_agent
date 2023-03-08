import requests
import enums
from jproperties import Properties  # config file
import json

class AuthenticatedAPI:
    def __init__(self, base_url, config_addr = None, model = enums.Model):
        self.base_url = base_url
        # load config file and then consume
        if(config_addr is not None):
            self.configs = self._load_configs(config_addr)
        # init for different model
        if model == enums.Model.RM:
            self.headers = {
            "Authorization": self._rm_login(),
            "Content-Type": "application/json"
            }
        elif model == enums.Model.RV:
            self.headers = {"X-API-Key": self.configs.get('X-API-Key').data}
        elif model == '':
            print('please select a model')

    def _load_configs(self, config_addr):
        # Load config file
        configs = Properties()
        try:
            with open(config_addr, 'rb') as config_file:
                configs.load(config_file)
        except:
            print("Error loading properties file, check the correct directory")

        return configs

    def _rm_login(self):
        base_url = "https://prod.robotmanager.com/api/v2"
        endpoint = "/login"
        payload = {}
        payload["username"] = "yongfeng@willsonic.com"
        payload["password"] = "NWcadcam2018!"
        payload["companyId"] = "16b6d42f-b802-4c0a-a015-ec77fc8a2108"

        headers = {"Content-Type":"application/json"}
        response = requests.post(url=base_url + endpoint, headers=headers, data=json.dumps(payload))
        return json.loads(response.text)["token"]

    def get(self, endpoint):
        url = self.base_url + endpoint
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
        
    def post(self, endpoint, json):
        url = self.base_url + endpoint
        try:
            response = requests.post(url, headers=self.headers, data=json)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
        
    def put(self, endpoint, json):
        url = self.base_url + endpoint
        try:
            response = requests.put(url, headers=self.headers, data=json)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
        
    def delete(self, endpoint):
        url = self.base_url + endpoint
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")

if __name__ == '__main__':
    # token = login()
    # print(token)

    rm_api = AuthenticatedAPI('https://prod.robotmanager.com/api/v2', model = enums.Model.RM)

    payload = {}
    payload["pageNo"] = 1
    payload["pageSize"] = 5
    payload["filter"] = []
    payload["order"] = [{"column":"created_at", "type":"desc"}]

    # res = rm_api.post('/robot/list', json.dumps(payload))
    # print(res)

    res = rm_api.get('/auth/loginInfo')
    print(res)

    rv_api = AuthenticatedAPI('http://rv-dev.eastasia.cloudapp.azure.com:8081/api', config_addr= '../../conf/nw/rv-config.properties',model = enums.Model.RV)

    res = rv_api.get('/battery/v1/state')
    print(res)
