import time
import logging, sys
import json
import uuid
# yf
import src.models.api_authenticated as api
import src.models.schema.rv as RVSchema
import src.utils.methods as umethods


class NWAPI(api.AuthenticatedAPI):
    def __init__(self, config):
        self.base_url = config.get('NWAPI', 'base_url')
        self.headers = {"Authorization": config.get('NWAPI', 'Authorization')[1:-1], "Content-Type": "application/json"}
        print(self.headers)
        super().__init__(base_url=self.base_url, headers=self.headers)

    def post_delivery_sms(self, phone_number, message):
        payload = {}
        payload["phone"] = phone_number
        payload["content"] = message
        print(json.dumps(payload))
        return self.post('/mission/delivery/sms/bynumber', json.dumps(payload))

    

if __name__ == '__main__':
    
    config = umethods.load_config('../../conf/config.properties')
    nwapi = NWAPI(config)

    phone_number = '+85293477398'
    message = "This is a test message~~"

    nwapi.post_delivery_sms(phone_number, message)