import requests
import json

base_url = "https://prod.robotmanager.com/api/v2"

def login():
    endpoint = "/login"
    payload = {}
    payload["username"] = "yongfeng@willsonic.com"
    payload["password"] = "NWcadcam2018!"
    payload["companyId"] = "16b6d42f-b802-4c0a-a015-ec77fc8a2108"

    headers = {"Content-Type":"application/json"}
    response = requests.post(url=base_url + endpoint, headers=headers, data=json.dumps(payload))
    return json.loads(response.text)["token"]
    
def robot_list(token, pageNo = 0, pageSize = 10):
    endpoint = "/robot/list"
    payload = {}
    payload["pageNo"] = pageNo
    payload["pageSize"] = pageSize
    payload["filter"] = []
    payload["order"] = [{"column":"created_at", "type":"desc"}]

    headers = {"Content-Type":"application/json", "Authorization":token}
    response = requests.post(url=base_url + endpoint, headers=headers, data=json.dumps(payload))
    print(response.text)

def list_map(token, pageNo = 1, pageSize = 10):
    endpoint = "/map/list"
    payload = {}
    payload["pageNo"] = pageNo
    payload["pageSize"] = pageSize
    payload["filter"] = []
    payload["order"] = [{"column":"created_at", "type":"desc"}]

    headers = {"Content-Type":"application/json", "Authorization":token}
    response = requests.post(url=base_url + endpoint, headers=headers, data=json.dumps(payload))

    # Parse the JSON response into a Python dictionary
    data = json.loads(response.text)

    # print(response.text)
    maps = data['result']['list']
    print(maps)

if __name__ == '__main__':
    token = login()
    # robot_list(token)
    list_map(token)