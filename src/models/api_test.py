import requests
import json

url = "http://192.168.7.34/api/v2.0.0/status"
headers = {
    "accept": "application/json",
    "Authorization": "Basic ZGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA==",
    "Accept-Language": "en_US",
    "Content-Type": "application/json"
}

payload = {
    "state_id": 3
}

response = requests.put(url, headers=headers, json=payload)

print(response.status_code)
print(response.json())  