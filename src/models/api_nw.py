import time
import logging, sys
import json
import uuid
import requests
# yf
import src.models.api_authenticated as api
import src.models.schema.rv as RVSchema
import src.utils.methods as umethods


class NWAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.base_url = config.get('NWAPI', 'base_url')
        self.headers = {"Authorization": "Bearer "+self.login(), "Content-Type": "application/json"}
        # print(self.headers)
        super().__init__(base_url=self.base_url, headers=self.headers)


    def login(self):
        base_url = 'https://dev-nv8am0mprp6tmtc7.us.auth0.com'
        endpoint = "/oauth/token"
        payload = {}
        payload["client_id"] = 'ojwilELEr73LKa7f1J2Y7y64LI5JZmVs'
        payload["client_secret"] = 'twSQD496LZgecsIH4bBMxbm12pBGtGRpkiBR1t97SC4Hzrbk4WHlYrGbbc2pUPh0'
        payload["audience"] = 'https://nwiapi.azurewebsites.net/'
        payload["grant_type"] = 'client_credentials'

        headers = {"Content-Type":"application/json"}
        response = requests.post(url=base_url + endpoint, headers=headers, data=json.dumps(payload))
        return json.loads(response.text)["access_token"]
    

    def post_delivery_sms(self, phone_number, message):
        payload = {}
        payload["phone"] = phone_number
        payload["content"] = message
        print(json.dumps(payload))
        return self.post('/mission/delivery/sms/bynumber', json.dumps(payload))

    

if __name__ == '__main__':
    
    config = umethods.load_config('../../conf/config.properties')
    nwapi = NWAPI(config)

    res = nwapi.login()
    print(res)

    phone_number = '+85293477398'
    message = "This is a test message~~~~~"

    nwapi.post_delivery_sms(phone_number, message)