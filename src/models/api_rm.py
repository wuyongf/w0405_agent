import api_authenticated as api
import json
import requests
import useful_functions.methods as um

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

    def getLoginInfo(self):
        return self.get('/auth/loginInfo')
    
    def getMapInfo(self):
        payload = {}
        payload["pageNo"] = 1
        payload["pageSize"] = 5
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]

        return self.post('/map/list', json.dumps(payload))

if __name__ == '__main__':
    config = um.load_config('../../conf/config.properties')
    rmapi = RMAPI(config)
    res = rmapi.getMapInfo()
    print(res)