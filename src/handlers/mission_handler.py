import threading
import time
import paho.mqtt.client as mqtt
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
from requests.exceptions import HTTPError
import requests
import logging
import json
# yf
import datetime
import src.models.api_rv as RVAPI
import src.models.api_rm as RMAPI
import src.models.db_robot as NWDB
import src.models.schema_rm as RMSchema
import src.models.schema_rv as RVSchema
import src.utils.methods as umethods

class MissionHandler:
    def __init__(self, config):
        self.robot_guid = config.get('NWDB','robot_guid')
        self.rmapi = RMAPI.RMAPI(config)
        self.mission_list = []
        self.job_list = []
        self.available_mission_list = []
        self.available_job_list = []

    ## RM side
    def get_mission_list(self):
        # # init
        self.mission_list.clear()
        # # get all missions
        json_data = self.rmapi.list_missions()
        # print(json_data)
        mission_list = json_data['result']['list']
        for mission in mission_list:
            if mission['robots'] is not None:
                for robot in mission['robots']:
                    if robot['id'] == self.robot_guid:
                        if(mission['type'] == 2):
                            self.mission_list.append(mission)
        return self.mission_list
    
    def get_job_list(self):
        # # init
        self.job_list.clear()
        # # get all missions
        json_data = self.rmapi.list_missions()
        # print(json_data)
        mission_list = json_data['result']['list']
        for mission in mission_list:
            if mission['robots'] is not None:
                for robot in mission['robots']:
                    if robot['id'] == self.robot_guid:
                        if(mission['type'] == 1):
                            self.job_list.append(mission)
        return self.job_list

    def get_available_mission_list(self):
        self.available_mission_list.clear()
        self.get_mission_list()
        for mission in self.mission_list:
            if(umethods.is_future_time(mission['scheduledAt'], umethods.get_current_time())):
                self.available_mission_list.append(mission)
        return self.available_mission_list

    def get_available_job_list(self):
            self.available_job_list.clear()
            self.get_job_list()
            for job in self.job_list:
                if(umethods.is_future_time(mission['scheduledAt'], umethods.get_current_time())):
                    self.available_job_list.append(mission)
            return self.available_job_list

    def pushlish_job_from_mission(self):
        pass

    def update_task_status(self):
        pass

    ## RV side
    def assign_task_to_rv(self):
        pass

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    mission_handler = MissionHandler(config)

    # list all missions and parse json
    # mission_handler.SortMissions()

    # job_list = mission_handler.get_job_list()
    avialable_mission_list = mission_handler.get_available_mission_list()
    
    # for mission in avialable_mission_list:
    #     print(mission)
    #     print(mission['name'])
    #     print(mission['scheduledAt'])

    mission = avialable_mission_list[0]
    print(mission)

    # get mission json

    # create a new job.
    # create serveral new RMSchema tasks.

    # create a RMSchema job and then dump as json
    # json_data = json.dumps(self.rm_status.__dict__, default=lambda o: o.__dict__)