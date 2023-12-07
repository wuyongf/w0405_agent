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
            if 'Content-Length' in response.headers:
                if response.headers['Content-Length'] == '0': 
                    print("[AuthenticatedAPI]: Empty JSON response received.") 
                    return None
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")

    def post(self, endpoint, json = None):
        url = self.base_url + endpoint
        try:
            response = requests.post(url, headers=self.headers, data=json)
            response.raise_for_status()
            if 'Content-Length' in response.headers:
                if response.headers['Content-Length'] == '0': 
                    print("[AuthenticatedAPI]: Empty JSON response received.") 
                    return None
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"[AuthenticatedAPI.post] Error: {error}")
            print(f"[AuthenticatedAPI.post] Error json: {json}")
        except requests.exceptions.HTTPError as http_error:
            status_code = http_error.response.status_code
            if status_code == 400:
                print(f"HTTP Error {status_code}: Bad Request - {http_error.response.text}")

    # def post(self, endpoint, json=None):
    #     url = self.base_url + endpoint
    #     try:
    #         response = requests.post(url, headers=self.headers, data=json)
    #         response.raise_for_status()


    #         if 'Content-Length' in response.headers:
    #             if response.headers['Content-Length'] == '0': 
    #                 print("[AuthenticatedAPI]: Empty JSON response received.") 

    #         return response.json()

    #     except requests.exceptions.RequestException as error:
    #         print(f"Error: {error}")

    #     except requests.exceptions.HTTPError as http_error:
    #         status_code = http_error.response.status_code
    #         if status_code == 400:
    #             print(f"HTTP Error {status_code}: Bad Request - {http_error.response.text}")
    #         elif status_code == 401:
    #             print(f"HTTP Error {status_code}: Unauthorized - {http_error.response.text}")
    #         # Add more specific error handling for other status codes if needed

        except ValueError as value_error:
            print(f"ValueError: {value_error}")

    def put(self, endpoint, json = None):
        url = self.base_url + endpoint
        try:
            response = requests.put(url, headers=self.headers, data=json)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                response_json = response.json()
                # Process the JSON data
            else:
                print("Response does not contain JSON data")
                response_json = None
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
        finally:
            return response_json
        
    def delete(self, endpoint):
        url = self.base_url + endpoint
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            content_length = response.headers.get('Content-Length')
            if content_length is not None and content_length == '0':
                print("[AuthenticatedAPI]: Empty JSON response received.")
                return None
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")

if __name__ == '__main__':
    # token = login()
    # print(token)

    rm_api = AuthenticatedAPI('https://prod.robotmanager.com/api/v2')

    payload = {}
    payload["pageNo"] = 1
    payload["pageSize"] = 5
    payload["filter"] = []
    payload["order"] = [{"column":"created_at", "type":"desc"}]

    # res = rm_api.post('/robot/list', json.dumps(payload))
    # print(res)

    res = rm_api.get('/auth/loginInfo')
    print(res)

    rv_api = AuthenticatedAPI('http://rv-dev.eastasia.cloudapp.azure.com:8081/api')

    res = rv_api.get('/battery/v1/state')
    print(res)
