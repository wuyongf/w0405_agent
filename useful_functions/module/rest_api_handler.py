import requests
import enums
from jproperties import Properties  # config file
import json

class AuthenticatedAPI:
    def __init__(self, base_url, config_addr, model = enums.Model):
        # load config file and then consume
        self.configs = self._load_configs(config_addr)
        # init for different model
        if model == enums.Model.RM:
            self.base_url = base_url
            self.headers = {
            "Authorization": f"Bearer {self.configs.get('rm_access_token').data}",
            "Content-Type": "application/json"
            }
        elif model == 'rv':
            pass
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
        
    def get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
        
    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
        
    def put(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
        
    def delete(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
base_url = 'https://prod.robotmanager.com/api/v2'
def login():
    endpoint = "/login"
    payload = {}
    payload["username"] = "yongfeng@willsonic.com"
    payload["password"] = "NWcadcam2018!"
    payload["companyId"] = "16b6d42f-b802-4c0a-a015-ec77fc8a2108"

    headers = {"Content-Type": "application/json"}
    response = requests.post(url=base_url + endpoint, headers=headers, data=json.dumps(payload))

    return json.loads(response.text)["token"]

if __name__ == '__main__':
    # token = login()
    # print(token)

    rm_api = AuthenticatedAPI('https://prod.robotmanager.com/api/v2',config_addr='config.properties', model = enums.Model.RM)

    payload = {}
    payload["pageNo"] = 1
    payload["pageSize"] = 5
    payload["filter"] = []
    payload["order"] = [{"column":"created_at", "type":"desc"}]
    data=json.dumps(payload)

    res = rm_api.post('/robot/list', data)
    print(res)