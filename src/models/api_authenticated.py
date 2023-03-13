import requests
# import useful_functions.module.enums_sys as enums_sys
from jproperties import Properties  # config file
import json

class AuthenticatedAPI:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

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
        
    def put(self, endpoint, json = {}):
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

    rm_api = AuthenticatedAPI('https://prod.robotmanager.com/api/v2', model = enums_sys.Model.RM)

    payload = {}
    payload["pageNo"] = 1
    payload["pageSize"] = 5
    payload["filter"] = []
    payload["order"] = [{"column":"created_at", "type":"desc"}]

    # res = rm_api.post('/robot/list', json.dumps(payload))
    # print(res)

    res = rm_api.get('/auth/loginInfo')
    print(res)

    rv_api = AuthenticatedAPI('http://rv-dev.eastasia.cloudapp.azure.com:8081/api', config_addr= '../../conf/nw/rv-config.properties',model = enums_sys.Model.RV)

    res = rv_api.get('/battery/v1/state')
    print(res)