import requests
from jproperties import Properties
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
            print(f"Error: {error}")
        
    def put(self, endpoint, json = None):
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
            if response.headers['Content-Length'] == '0': 
                print("[AuthenticatedAPI]: Empty JSON response received.") 
                return None
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"Error: {error}")
