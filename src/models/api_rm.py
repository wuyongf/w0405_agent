import sys
import json
import requests
import src.models.api_authenticated as api
import src.models.enums.rm as RMEnum
import src.models.schema.rm as RMSchema
import src.utils.methods as umethods
from src.models.trans import RMLayoutMapTransform

class RMAPI(api.AuthenticatedAPI):
    def __init__(self, config, skill_config_dir):
        self.config = config
        self.base_url = self.config.get('RM','base_url')
        self.headers = {
            "Authorization": self.__login(),
            "Content-Type": "application/json"
            }
        super().__init__(base_url=self.base_url, headers=self.headers)

        # robot
        self.robot_guid = self.config.get('NWDB','robot_rm_guid')

        self.__write_robot_skill_to_properties(self.robot_guid, skill_config_dir)
        self.skill_config = umethods.load_config(skill_config_dir)

        self.T_rmapi = RMLayoutMapTransform()
    
    ### [login]
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

    def __write_robot_skill_to_properties(self,robotId, skill_config_dir):
        # http://dev.robotmanager.io/api/v2/robot-skills

        # robotId = "2658a873-a0a6-4c3f-967f-d179c4073272" # "2658a873-a0a6-4c3f-967f-d179c4073272"
        # robot-skills/get-by-robot/{robotId}
        data = self.get(f'/robot-skills/get-by-robot/{robotId}')
        results = data['result']

        with open(skill_config_dir, 'w') as config_file:
            config_file.write('[RM-Skill]' + '\n')
            # Iterate over each item and extract the "id" and "name"
            for item in results:
                item_id = item['id']
                item_name = item['name']
                item_name = item_name.replace(' ', '-')
                config_file.write(f'{item_name} = {item_id}' + '\n')
                # print(f'skill: {item_name}  skill_id: {item_id}')

    def write_rm_map_to_properties(self,rm_map_dir):
        # http://dev.robotmanager.io/api/v2/robot-skills

        # robotId = "2658a873-a0a6-4c3f-967f-d179c4073272" # "2658a873-a0a6-4c3f-967f-d179c4073272"
        # robot-skills/get-by-robot/{robotId}
        # data = self.get(f'/robot-skills/get-by-robot/{robotId}')
        data = self.list_maps()
        results = data['result']["list"]

        with open(rm_map_dir, 'w') as config_file:
            config_file.write('[RM-MAP-GUID]' + '\n')
            # Iterate over each item and extract the "id" and "name"
            for item in results:
                item_id = item['id']
                item_name = item['name']
                item_name = item_name.replace(' ', '-')
                config_file.write(f'{item_name} = {item_id}' + '\n')
                # print(f'skill: {item_name}  skill_id: {item_id}')

    def get_login_info(self):
        return self.get('/auth/loginInfo')
    
    ### [mission]
    def list_missions(self):
        payload = {}
        payload["pageNo"] = sys.maxsize
        payload["pageSize"] = sys.maxsize
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]
        return self.post('/mission/list', json.dumps(payload))
    
    def list_rm_missions(self):
        
        data = self.list_missions()

        results = data['result']['list']
        # Iterate over each item
        rm_missions = []
        for item in results:
            if(item['type'] == 2):
                rm_missions.append(item)
        return rm_missions

    def update_rm_mission(self):
        
        def convertDate(year, month, day, hour, minute, second, offset_hours):
            from datetime import datetime, timezone, timedelta

            # Create a datetime object
            
            dt = datetime(year, month, day, hour, minute, second, tzinfo=timezone(timedelta(hours=offset_hours)))

            # Format the datetime object as ISO 8601
            formatted_time = dt.isoformat()

            formatted_time_with_z = formatted_time.replace('+00:00', 'Z')
            # print(formatted_time_with_z)
            return formatted_time_with_z

        def getCurrentDate():
            # Get the current time
            current_time = datetime.utcnow()  # Use utcnow to get UTC time

            # # Extract components
            # year = current_time.year
            # month = current_time.month
            # day = current_time.day
            # hour = current_time.hour
            # minute = current_time.minute
            # second = current_time.second

            return current_time

        # start time
        start_time = convertDate(2024,1,12,17,1,40,8)
        end_time = convertDate(2024,1,12,17,50,0,20)

        payload = {}
        payload["mode"] = 3
        # payload["layoutId"] = '00000000-0000-0000-0000-000000000000'#'0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d'#
        # payload["layoutName"] = "6F-Layout"
        payload['id'] = '45675968-fa97-4776-8e20-ed24e1b02014'
        # payload["name"] = 'ChargingOffOn'
        payload["startTime"]   = start_time #'2024-01-12T12:37:00Z'
        payload["scheduledAt"] = start_time #'2024-01-12T12:37:00Z'
        payload["status"] = 4
        payload["repeatType"] = 1
        return self.put('/mission/update', json.dumps(payload))

    def new_mission(self, robot_id, layout_id = '', mission_name = 'New Mission Demo', tasks = []):
        '''ref: https://docs.robotmanager.com/reference/create-a-mission'''
        payload = {}
        payload["type"] = 2
        # payload["mode"] = 1
        payload["layoutId"] = layout_id
        payload["name"] = mission_name
        payload["robotIds"] = [f'{robot_id}'] # 2658a873-a0a6-4c3f-967f-d179c4073272
        payload['tasks'] = tasks
        return self.post('/mission', json.dumps(payload))
    
    def delete_mission(self, mission_id):
        return self.delete(f'/mission/{mission_id}')
    
    def get_mission_id(self, task_json):
        # self.__init__()
        json_data = self.list_missions()
        # print(json_data)
        if json_data is not None:
            list_data = json_data['result']['list']
            # print(list_data)
            for mission in list_data:
                # taskId == mission['tasks']['id']
                if mission['tasks'] is None: continue
                else:
                    for task in mission['tasks']:
                        if (task_json['taskId'] == task['id']):
                            return mission['id']
        else: 
            print('[api_rm.get_mission_id]: cannot find the mission_id')
            return None

    ### [task]
    def new_task(self, skill_id, layout_id, layoutMarkerId = None, order = 1):
            
        task = {
            "skillId": skill_id,
            "layoutId": layout_id,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            # "params": [{"paramKey": "positionName", "paramValue": "delivery-01"}]
        }

        return task

    def new_task_delivery_goto(self, map_rm_guid, layoutMarkerName = None, layout_heading = 0, order = 1):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'DELIVERY-GOTO')
        
        params = self.get_layout_map_list(layout_guid, map_rm_guid)
        self.T_rmapi.update_layoutmap_params(params.imageWidth, params.imageHeight,params.scale, params.angle, params.translate)

        layoutMarkerId, layout_x, layout_y = self.get_layout_marker_detail(layout_guid, layoutMarkerName)
        map_x, map_y, map_heading = self.T_rmapi.find_cur_map_point(layout_x, layout_y, layout_heading)

        def goto_params(map_id, pos_name, x, y, heading):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            params = [param_map, param_name, param_x, param_y, param_heading]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            "params": goto_params(map_rm_guid, layoutMarkerName, map_x, map_y, map_heading)
        }     

        return task

    def new_task_goto(self, map_rm_guid, layoutMarkerName = None, layout_heading = 0, order = 1):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'NW-GOTO-DEFAULT')
        
        params = self.get_layout_map_list(layout_guid, map_rm_guid)
        self.T_rmapi.update_layoutmap_params(params.imageWidth, params.imageHeight,params.scale, params.angle, params.translate)

        layoutMarkerId, layout_x, layout_y = self.get_layout_marker_detail(layout_guid, layoutMarkerName)
        map_x, map_y, map_heading = self.T_rmapi.find_cur_map_point(layout_x, layout_y, layout_heading)
    
        # print(f'layoutMarkerId: {layoutMarkerId}')
        # print(f'layout_x: {layout_x}')
        # print(f'layout_y: {layout_y}')

        # def goto_params2(pos_name):
        #     params = []
        #     param_name = {"paramKey": "POINT1", "paramValue": str(pos_name)}
        #     params = [param_name]
        #     return params

        def goto_params(map_id, pos_name, x, y, heading):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            params = [param_map, param_name, param_x, param_y, param_heading]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            # "params": goto_params2(layoutMarkerName)
            "params": goto_params(map_rm_guid, layoutMarkerName, map_x, map_y, map_heading)
        }     

        return task

    def new_task_localize(self, map_rm_guid, layoutMarkerName = None, layout_heading = 0, order = 1):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'RM-LOCALIZE')

        params = self.get_layout_map_list(layout_guid, map_rm_guid)
        self.T_rmapi.update_layoutmap_params(params.imageWidth, params.imageHeight,params.scale, params.angle, params.translate)

        layoutMarkerId, layout_x, layout_y = self.get_layout_marker_detail(layout_guid, layoutMarkerName)
        map_x, map_y, map_heading = self.T_rmapi.find_cur_map_point(layout_x, layout_y, layout_heading)

        def position_params(map_id, pos_name, x, y, heading):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            params = [param_map, param_name, param_x, param_y, param_heading]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            "params": position_params(map_rm_guid, layoutMarkerName, map_x, map_y, layout_heading)
        }     

        return task

    def new_task_delivery_post_localize(self, map_rm_guid, layoutMarkerName = None, layout_heading = 0, order = 1):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'DELIVERY-POST-LOCALIZE')

        params = self.get_layout_map_list(layout_guid, map_rm_guid)
        self.T_rmapi.update_layoutmap_params(params.imageWidth, params.imageHeight,params.scale, params.angle, params.translate)

        layoutMarkerId, layout_x, layout_y = self.get_layout_marker_detail(layout_guid, layoutMarkerName)
        map_x, map_y, map_heading = self.T_rmapi.find_cur_map_point(layout_x, layout_y, layout_heading)

        def position_params(map_id, pos_name, x, y, heading):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            params = [param_map, param_name, param_x, param_y, param_heading]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            "params": position_params(map_rm_guid, layoutMarkerName, map_x, map_y, layout_heading)
        }     

        return task
    
    def new_task_lift_to(self, map_rm_guid, order = 1, 
                         target_floor = 0, hold_min =10):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'NW-LIFT-TO')

        def custom_params(target_floor, hold_min):
            params = []
            param_target_floor = {"paramKey": "target_floor", "paramValue": target_floor}
            param_hold_min = {"paramKey": "hold_min", "paramValue": hold_min}
            params = [param_target_floor, param_hold_min]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "executionType": 1, # 1: series 2: parallel
            "params": custom_params(target_floor, hold_min)
        }

        return task
    
    def new_task_lift_levelling(self, map_rm_guid, order = 1, 
                         current_floor = 0):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'LIFT-LEVLLING')

        def custom_params(current_floor):
            params = []
            param_current_floor = {"paramKey": "current_floor", "paramValue": current_floor}
            params = [param_current_floor]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "executionType": 1, # 1: series 2: parallel
            "params": custom_params(current_floor)
        }

        return task

    def new_task_nw_lift_in(self, map_rm_guid, layoutMarkerName = None, order = 1, 
                            layout_heading = 0, current_floor = 4, target_floor =6):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'NW-LIFT-IN')

        params = self.get_layout_map_list(layout_guid, map_rm_guid)
        self.T_rmapi.update_layoutmap_params(params.imageWidth, params.imageHeight,params.scale, params.angle, params.translate)

        layoutMarkerId, layout_x, layout_y = self.get_layout_marker_detail(layout_guid, layoutMarkerName)
        map_x, map_y, map_heading = self.T_rmapi.find_cur_map_point(layout_x, layout_y, layout_heading)

        def position_params(map_id, pos_name, x, y, heading, current_floor, target_floor):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            param_current_floor = {"paramKey": "current_floor", "paramValue": current_floor}
            param_target_floor = {"paramKey": "target_floor", "paramValue": target_floor}
            params = [param_map, param_name, param_x, param_y, param_heading, param_current_floor, param_target_floor]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            "params": position_params(map_rm_guid, layoutMarkerName, map_x, map_y, map_heading,current_floor,target_floor)
        }     

        return task

    def new_task_nw_lift_out(self, map_rm_guid, layoutMarkerName = None, layout_heading = 0, order = 1):
        
        layout_guid =  self.get_layout_guid(map_rm_guid)
        skill_id = self.skill_config.get('RM-Skill', 'NW-LIFT-OUT')
        
        params = self.get_layout_map_list(layout_guid, map_rm_guid)
        self.T_rmapi.update_layoutmap_params(params.imageWidth, params.imageHeight,params.scale, params.angle, params.translate)

        layoutMarkerId, layout_x, layout_y = self.get_layout_marker_detail(layout_guid, layoutMarkerName)
        map_x, map_y, map_heading = self.T_rmapi.find_cur_map_point(layout_x, layout_y, layout_heading)

        def goto_params(map_id, pos_name, x, y, heading):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            params = [param_map, param_name, param_x, param_y, param_heading]
            return params

        task = {
            "skillId": skill_id,
            "layoutId": layout_guid,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            # "params": goto_params2(layoutMarkerName)
            "params": goto_params(map_rm_guid, layoutMarkerName, map_x, map_y, map_heading)
        }     

        return task

    def task_goto(self, skill_id, layout_id, layoutMarkerId = None, order = 1, 
                  map_id = None, pos_name = None, x = None, y = None, heading = None):
        
        def goto_params(map_id, pos_name, x, y, heading):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            params = [param_map, param_name, param_x, param_y, param_heading]
            return params
            
        task = {
            "skillId": skill_id,
            "layoutId": layout_id,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            "params": goto_params(map_id, pos_name, x, y, heading)
        }

        return task
    
    def task_localize(self, skill_id, layout_id, layoutMarkerId = None, order = 1, 
                  map_id = None, pos_name = None, x = None, y = None, heading = None):
        
        def goto_params(map_id, pos_name, x, y, heading):
            params = []
            param_map = {"paramKey": "mapId", "paramValue": str(map_id)}
            param_name = {"paramKey": "positionName", "paramValue": str(pos_name)}
            param_x = {"paramKey": "x", "paramValue": x}
            param_y = {"paramKey": "y", "paramValue": y}
            param_heading = {"paramKey": "heading", "paramValue": heading}
            params = [param_map, param_name, param_x, param_y, param_heading]
            return params
            
        task = {
            "skillId": skill_id,
            "layoutId": layout_id,
            "order": order,
            "layoutMakerId": layoutMarkerId,
            "executionType": 1, # 1: series 2: parallel
            "params": goto_params(map_id, pos_name, x, y, heading)
        }

        return task

    ### [miscellaneous]
    def list_maps(self):
        payload = {}
        payload["pageNo"] = 1
        payload["pageSize"] = 10
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]
        return self.post('/map/list', json.dumps(payload))

    def list_robot_skill(self):
        # http://dev.robotmanager.io/api/v2/robot-skills

        robotId = "2658a873-a0a6-4c3f-967f-d179c4073272"
        # robot-skills/get-by-robot/{robotId}
        data = self.get(f'/robot-skills/get-by-robot/{robotId}')

        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            print(f'skill: {item_name}  skill_id: {item_id}')
    
    def list_layouts(self):
        payload = {}
        payload["pageNo"] = 1
        payload["pageSize"] = 10
        payload["filter"] = []
        payload["order"] = [{"column":"created_at", "type":"desc"}]
        data = self.post('/layouts/list', json.dumps(payload))
        results = data['result']['list']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            print(f'layout: {item_name}  id: {item_id}')

    def get_layout_guid(self, map_guid):
        data = self.list_maps()
        results = data['result']['list']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            if item['layout'] is None: continue
            else:
                item_id = item['id']
                item_layout_id = item['layout']['id']
                if item_id == map_guid:
                    return item_layout_id

    def list_layout_markers(self, layout_id):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        # layout_id = "ca0ac9aa-9910-4949-90d5-6efb525015b7"
        data = self.get(f'/layout-markers/{layout_id}')

        results = data['result']
        print(results)
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            item_position = item['position']
            print(f'marker: {item_name}  id: {item_id} position: {item_position}')
        return results
    
    def create_layout_marker(self, layout_id, name):
        payload = {}
        payload["layoutId"] = layout_id
        payload["name"] = name
        payload["position"] = {"x": 20,"y": 20,"z": 0}
        return self.post('/layout-markers', json.dumps(payload))
        pass
    
    def delete_layout_marker(self, id):
        return self.delete(f'/layout-markers/{id}')
        pass

    def get_layout_marker_detail(self, layout_guid, position_name):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        # layout_id = "ca0ac9aa-9910-4949-90d5-6efb525015b7"
        data = self.get(f'/layout-markers/{layout_guid}')

        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_x  = item['position']['x']
            item_y  = item['position']['y']
            item_name = item['name']
            if position_name == item_name:
                return item_id, item_x, item_y
    
    def get_layout_marker(self, layout_guid, position_name):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        # layout_id = "ca0ac9aa-9910-4949-90d5-6efb525015b7"
        data = self.get(f'/layout-markers/{layout_guid}')

        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            # item_id = item['id']
            item_name = item['name']
            if position_name == item_name:
                return item
    
    def get_layout_map_list(self, layoutIds, mapIds):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        payload = {}
        # payload["layoutIds"] = ['0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d']
        # payload["mapIds"] = [f'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a']
        payload["layoutIds"] = [layoutIds]
        payload["mapIds"] = [mapIds]
        data = self.post('/layouts-map/list', json.dumps(payload))

        calibrationData_string = data['result'][0]['calibrationData']
        calibrationData = json.loads(calibrationData_string)
        
        # layoutWidth = calibrationData['layoutWidth']
        # layoutHeight = calibrationData['layoutHeight']
        imageWidth = calibrationData['imageWidth']
        imageHeight = calibrationData['imageHeight']
        scale = calibrationData['transform']['scale']
        angle = calibrationData['transform']['angle']        
        translate = calibrationData['transform']['translate']

        # print(f'calibrationData: {calibrationData}')  

        layout_map_list  =  RMSchema.LayoutMapList(imageWidth, imageHeight, scale, angle, translate)
        return layout_map_list

    ### [door]
    def list_layout_doors(self, layout_id):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        # layout_id = "ca0ac9aa-9910-4949-90d5-6efb525015b7"
        data = self.get(f'/door?layoutId={layout_id}')

        results = data['result']
        # # Iterate over each item and extract the "id" and "name"
        # for item in results:
        #     item_id = item['id']
        #     item_name = item['name']
        #     item_position = item['position']
        #     print(f'marker: {item_name}  id: {item_id} position: {item_position}')
        return results
    
    def new_job_configure_delivery(self, robot_id):
        '''ref: https://docs.robotmanager.com/reference/create-a-mission'''
        payload = {}
        payload["type"] = 1 # 1: job 2: mission
        payload["mode"] = 1 # 1:Execute immediately
        payload["layoutId"] = ''
        payload["name"] = 'Configure Delivery Mission'
        payload["robotIds"] = [f'{robot_id}'] # 2658a873-a0a6-4c3f-967f-d179c4073272
        payload['tasks'] = [
        {
            "skillId": "354a542a-2227-4b74-be44-41cd7b6dcf2c",
            "layoutId": "ca0ac9aa-9910-4949-90d5-6efb525015b7",
            "order": 1,
            "layoutMakerId": 1
        }]
        return self.post('/mission', json.dumps(payload))

    def new_job(self, robot_id, layout_id = '', tasks = [], job_name = 'New Job Demo'):
        '''ref: https://docs.robotmanager.com/reference/create-a-mission'''
        payload = {}
        payload["type"] = 1 # 1: job 2: mission
        payload["mode"] = 1 # 1:Execute immediately
        payload["layoutId"] = layout_id
        payload["name"] = job_name
        payload["robotIds"] = [f'{robot_id}'] # 2658a873-a0a6-4c3f-967f-d179c4073272
        payload['tasks'] = tasks
        print(f'[api_rm.new_job] payload: {payload}')
        res = self.post('/mission', json.dumps(payload))
        return res

    ### [delivery]
    
    def create_delivery_marker(self, layout_id, x, y, heading):
        
        delivery_names = []
        count = 0
        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            item_position = item['position']
            if "delivery" in item_name.lower():
                delivery_names.append(item_name)

        if len(delivery_names) == 0: count = 1
        else: 
            sorted_delivery_names = sorted(delivery_names)
            numeric_values = [int(item.split('-')[1]) for item in sorted_delivery_names]
            largest_number = max(numeric_values)
            count = largest_number+1

        payload = {}
        payload["layoutId"] = layout_id
        formatted_number = '{:02}'.format(count)
        payload["name"] = f'delivery-{formatted_number}'
        payload["position"] = {"x": x,"y": y,"z": heading}

        self.post('/layout-markers', json.dumps(payload))
        return payload["name"]

    def get_delivery_markers(self, layout_id):
        # https://docs.robotmanager.com/reference/find-makers-by-layout

        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            item_position = item['position']
            if "delivery" in item_name.lower():
                print(f'marker: {item_name}  id: {item_id} position: {item_position}')
        return results
    
    def get_latest_delivery_marker_guid(self, layout_id):
        delivery_markers = {}
        count = 0
        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            if "delivery" in item_name.lower():
                delivery_markers[item_name] = item_id

        if len(delivery_markers) == 0:
            print('cannot find any delivery marker!')
            return None
        else: 
            sorted_delivery_names = sorted(delivery_markers)
            numeric_values = [int(item.split('-')[1]) for item in sorted_delivery_names]
            largest_number = max(numeric_values)
            formatted_number = '{:02}'.format(largest_number)
            guid = delivery_markers[f'delivery-{formatted_number}']
            print(f'found latest delivery marker guid: {guid}')
            return guid

    def delete_all_delivery_markers(self, layout_id):
        data = self.get(f'/layout-markers/{layout_id}')
        results = data['result']
        # Iterate over each item and extract the "id" and "name"
        for item in results:
            item_id = item['id']
            item_name = item['name']
            if "delivery" in item_name.lower():
                self.delete_layout_marker(item_id)

    def new_job_demo(self):
        '''ref: https://docs.robotmanager.com/reference/create-a-mission'''
        payload = {}
        payload["type"] = 1 # 1: job 2: mission
        payload["mode"] = 1 # 1:Execute immediately
        payload["layoutId"] = 'ca0ac9aa-9910-4949-90d5-6efb525015b7'
        payload["name"] = 'Configure Delivery Mission'
        payload["robotIds"] = ['2658a873-a0a6-4c3f-967f-d179c4073272'] # 2658a873-a0a6-4c3f-967f-d179c4073272
        payload['tasks'] = [
        {
            "skillId": "f8919eca-c5f2-4b33-8efd-d2222107cfba",
            "layoutId": "ca0ac9aa-9910-4949-90d5-6efb525015b7",
            "order": 1,
            "layoutMakerId": 'f8919eca-c5f2-4b33-8efd-d2222107cfba',
            "params": [{"paramKey": "positionName", "paramValue": "delivery-01"}]
        }]
        print(payload)
        return self.post('/mission', json.dumps(payload))

    def get_latest_mission_status(self):
        json_data = self.list_missions()
        # print(json_data)
        list_data = json_data['result']['list']
        value = list_data[0]['status']

        return RMEnum.MissionStatus(value)
    
    def get_latest_mission(self):
        json_data = self.list_missions()
        # print(json_data)
        list_data = json_data['result']['list']
        return list_data[0]

def goto_charging_staion():
    config = umethods.load_config('../../conf/config.properties')
    rmapi = RMAPI(config)

    import src.models.db_robot as RobotDB
    nwdb = RobotDB.robotDBHandler(config)

    import src.models.trans as Trans
    T_RM = Trans.RMLayoutMapTransform()

    map_rm_guid = 'c5f360ec-f4be-4978-a281-0a569dab1174'
    layout_guid = '3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece'
    params = rmapi.get_layout_map_list(layout_guid, map_rm_guid)
    T_RM.update_layoutmap_params(params.imageWidth, params.imageHeight, 
                                              params.scale, params.angle, params.translate)

    ##############
    # Publish GOTO Mission
    ##############
    charging_station_id = nwdb.get_available_charging_station_id(1)
    charging_station = nwdb.get_charing_station_detail(charging_station_id)

    map_x, map_y, map_heading = T_RM.find_cur_map_point(charging_station.pos_x, charging_station.pos_y, charging_station.pos_theta)
    print(f'[charging_goto]: goto...')
    # Job-Delivery START
    # TASK START
    tasks = []
    rmapi.delete_all_delivery_markers(charging_station.layout_rm_guid)
    # configure task-01: create a new position on RM-Layout
    rmapi.create_delivery_marker(charging_station.layout_rm_guid, map_x, map_y, map_heading)
    print(f'layout_rm_guid: {charging_station.layout_rm_guid}')
    latest_marker_id = rmapi.get_latest_delivery_marker_guid(charging_station.layout_rm_guid)
    print(f'latest_marker_id: {latest_marker_id}')
    # configure task-01: create a new task
    goto = rmapi.task_goto('f8919eca-c5f2-4b33-8efd-d2222107cfba',
                                charging_station.layout_rm_guid,
                                latest_marker_id,
                                order=1,
                                map_id=charging_station.map_rm_guid,
                                pos_name=charging_station.pos_name,
                                x=map_x,
                                y=map_y, 
                                heading=map_heading)
    tasks.append(goto)
    print(goto)
    # TASK END
    print(f'[new_delivery_mission]: configure task end...')
    rmapi.new_job('2658a873-a0a6-4c3f-967f-d179c4073272', charging_station.layout_rm_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
    print(f'[new_delivery_mission]: configure job end...')

def pub_localization():
    config = umethods.load_config('../../conf/config.properties')
    rmapi = RMAPI(config)

    import src.models.db_robot as RobotDB
    nwdb = RobotDB.robotDBHandler(config)

    import src.models.trans as Trans
    T_RM = Trans.RMLayoutMapTransform()

    map_rm_guid = 'c5f360ec-f4be-4978-a281-0a569dab1174'
    layout_guid = '3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece'

    params = rmapi.get_layout_map_list(layout_guid, map_rm_guid)
    T_RM.update_layoutmap_params(params.imageWidth, params.imageHeight,params.scale, params.angle, params.translate)

    ##############
    # Publish GOTO Mission
    ##############
    charging_station_id = nwdb.get_available_charging_station_id(1)
    charging_station = nwdb.get_charing_station_detail(charging_station_id)
    map_x, map_y, map_heading = T_RM.find_cur_map_point(charging_station.pos_x, charging_station.pos_y, charging_station.pos_theta)
    print(f'[charging_goto]: goto...')
    # Job-Delivery START
    # TASK START
    tasks = []
    rmapi.delete_all_delivery_markers(charging_station.layout_rm_guid)
    # configure task-01: create a new position on RM-Layout
    rmapi.create_delivery_marker(charging_station.layout_rm_guid, map_x, map_y, map_heading)
    print(f'layout_rm_guid: {charging_station.layout_rm_guid}')
    latest_marker_id = rmapi.get_latest_delivery_marker_guid(charging_station.layout_rm_guid)
    print(f'latest_marker_id: {latest_marker_id}')
    # configure task-01: create a new task
    goto = rmapi.task_localize('cc8ab9bc-3462-4552-ac3b-783f1b944c0c',
                                charging_station.layout_rm_guid,
                                latest_marker_id,
                                order=1,
                                map_id=charging_station.map_rm_guid,
                                pos_name='TEMP',
                                x=map_x,
                                y=map_y, 
                                heading=map_heading)
    tasks.append(goto)
    print(goto)
    # TASK END
    print(f'[new_delivery_mission]: configure task end...')
    rmapi.new_job('2658a873-a0a6-4c3f-967f-d179c4073272', charging_station.layout_rm_guid, tasks=tasks, job_name='Localize-DEMO')
    print(f'[new_delivery_mission]: configure job end...')

dict_map_guid = {
    999: "1f7f78ab-5a3b-467b-9179-f7508a99ad6e",
    7: "5f5efd43-8140-43e6-9492-996b8158fe49",
    6: "d6734e98-f53a-4b69-8ed8-cbc42ef58e3a",
    5: "454ff88a-c680-4910-a6ee-72a2da44c148",
    4: "c5f360ec-f4be-4978-a281-0a569dab1174",
    3: "5df44de9-3ed6-4851-b67a-140256855279",
    2: "2301bb6e-4c4a-4660-af79-e5583955fb32",
    1: "c96fd506-ceb0-47ab-908c-2ac043a861c7",
    0: "d6c31219-5fba-4e94-b651-3e26c9bf43b2"
}

if __name__ == '__main__':

    # pub_localization()
    # goto_charging_staion()
    from datetime import datetime



    ### [Mission]
    # 1) init

    skill_config_dir = '../../conf/rm_skill.properties'
    config = umethods.load_config('../../conf/config.properties')
    rmapi = RMAPI(config, skill_config_dir)


    rmapi.update_rm_mission()

    res = rmapi.list_rm_missions()
    print(res)

    # robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
    # map_rm_guid = 'c5f360ec-f4be-4978-a281-0a569dab1174'
    # layout_rm_guid =  rmapi.get_layout_guid(map_rm_guid)  # 3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece
    # print(layout_rm_guid)

    # # res = rmapi.get_layout_marker(layout_guid, 'P0')
    # # print(res)
    # # rmapi.write_rm_map_to_properties("../../conf/rm_map.properties")
    # # res= rmapi.get_layout_marker(layout_rm_guid, 'LiftWaitingPoint')
    # # print(res)

    # # rmapi.write_robot_skill_to_properties(robot_rm_guid, skill_config_dir)
    # skill_config = umethods.load_config(skill_config_dir)

    # # # 2) implement task detail
    # rv_charging_on = rmapi.new_task(skill_config.get('RM-Skill', 'RV-CHARGING-ON'), layout_rm_guid)
    # rv_charging_off = rmapi.new_task(skill_config.get('RM-Skill', 'RV-CHARGING-OFF'), layout_rm_guid)
    # iaq_on = rmapi.new_task(skill_config.get('RM-Skill', 'IAQ-ON'), layout_rm_guid)
    # iaq_off = rmapi.new_task(skill_config.get('RM-Skill', 'IAQ-OFF'), layout_rm_guid)
    # localize1 = rmapi.new_task_localize(map_rm_guid, 'ChargingStation', layout_heading=180)
    # goto1 = rmapi.new_task_goto(map_rm_guid, "P0", layout_heading= 90)
    # goto2 = rmapi.new_task_goto(map_rm_guid, "P1", layout_heading= 90)
    # goto_dock = rmapi.new_task_goto(map_rm_guid, "ChargingStation", layout_heading= 180)

    # def new_task_take_lift(current_floor_id, target_floor_id):
        
    #     current_map_rm_guid = dict_map_guid[current_floor_id]
    #     target_map_rm_guid = dict_map_guid[target_floor_id]
    #     lift_map_rm_guid = dict_map_guid[999]

    #     tasks = []
        
    #     task1 = rmapi.new_task_goto(current_map_rm_guid, "LiftWaitingPoint", layout_heading= 0)
    #     task2 = rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint', layout_heading= 90)
        
    #     if(current_floor_id == 0):
    #         task_in = rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
    #     else:
    #         task_in = rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
        
    #     if(target_floor_id == 0):
    #         task_out = rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint-G', layout_heading= 90)
    #     else:
    #         task_out = rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint', layout_heading=270)

    #     task3 = rmapi.new_task_localize(target_map_rm_guid, 'LiftWaitingPoint', layout_heading= 180)

    #     tasks.append(task1)
    #     tasks.append(task2)
    #     tasks.append(task_in)
    #     tasks.append(task_out)
    #     tasks.append(task3)

    #     return tasks

    # # 3) new task
    # tasks = new_task_take_lift(4,6)

    # # tasks.append(rv_charging_off)
    # # tasks.append(localize1)
    # # tasks.append(iaq_on)
    # # tasks.append(goto1)
    # # tasks.append(goto2)
    # # tasks.append(goto_dock)
    # # tasks.append(iaq_off)
    # # tasks.append(rv_charging_on)

    # # 4) new mission
    # mission_name = 'LiftAccess-4to6'
    # rmapi.new_mission(robot_rm_guid, layout_rm_guid, mission_name, tasks)
    



    ### [mission]
    ### 7/F: Q0 ~ Q5
    ### 6/F: Q0 ~ Q12

    # res = rmapi.get_latest_mission()
    # print(res)

    # res = rmapi.delete_all_delivery_markers('3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece')

    # ##############
    # # List Doors
    # ##############
    # json_door = rmapi.list_layout_doors('3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece')
    
    # door_list = []
    # for item in json_door:

    #     door  = RMSchema.Door.parse(item)

    #     door_list.append(door)

    # print('done')

    # json(json_door)
    # print(res)

    ##############
    # List Layout Markers
    ##############
    # res = rmapi.list_layout_doors('3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece')
    # print(res)

    #  6df33060-c51b-445b-a07e-86b8d5b3bcda
    # res = rmapi.list_maps()
    # print(res)

    # res = rmapi.list_layouts()
    # print('========================')

    # 4F-map: 
    # 4F-layout : 3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece
    
    

    # res = rmapi.get_layout_map_list(layoutIds='3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece', mapIds='c5f360ec-f4be-4978-a281-0a569dab1174')
    # print(res)
    # c5f360ec-f4be-4978-a281-0a569dab1174
    # res = rmapi.get_layout_guid('3bc4db02-7bb4-4bbc-9e0c-8e0c1ddc8ece')
    # print(res)

    # res = rmapi.list_maps()
    # print(res)
    # rmapi.new_job_demo()

    # res = rmapi.get_layout_guid(map_guid='1e28ee6e-2fc4-4d72-bed5-8d1a421783ff')
    # print(res) # 76186080-1adb-4542-b2be-4a5b112a6b86

    # rmapi.list_layout_markers('76186080-1adb-4542-b2be-4a5b112a6b86')
    # res = rmapi.get_layout_marker_guid('76186080-1adb-4542-b2be-4a5b112a6b86','P0')
    # print(res)  #210626fe-917c-480a-bdf0-3b5012d4a1b2

    # json_data = rmapi.new_job()
    # print(json_data)
    
    # rmapi.list_robot_skill()
    
    # res = rmapi.list_layouts()
    # print(res)

    # rmapi.create_layout_marker('ca0ac9aa-9910-4949-90d5-6efb525015b7', 'delivery-03')
    # rmapi.list_layout_markers('ca0ac9aa-9910-4949-90d5-6efb525015b7')
    # rmapi.delete_layout_marker('5d22bc53-4c62-4757-9c2f-98d3cf2d8393')
    # rmapi.list_layout_markers()

    # # # Delivery
    # rmapi.create_delivery_marker(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7', x=20, y=20, heading=0)
    # rmapi.delete_all_delivery_markers(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7')
    # # rmapi.get_delivery_markers(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7')
    # # rmapi.get_latest_delivery_marker_guid(layout_id='ca0ac9aa-9910-4949-90d5-6efb525015b7')

    # # retrieve skills and get skill_config
    # rmapi.write_robot_skill_to_properties(robotId="2658a873-a0a6-4c3f-967f-d179c4073272")
    # skill_config = umethods.load_config('./conf/rm_skill.properties')
    
    # # get destination_id and then create a rm_guid first.

    # # initiate delivery mission
    # tasks = []
    # goto_01 = rmapi.new_task(skill_config.get('RM-Skill','RM-GOTO'), )
    # tasks.append(goto_01)
    
    # rmapi.new_job(robotId="2658a873-a0a6-4c3f-967f-d179c4073272", layout_id='', tasks = tasks, job_name='DELIVERY-GOTO-DEMO')

    # # # Delivery End

    # json_data = rmapi.create_mission()
    # print(json_data)

    # ## list map
    # json_data = rmapi.list_maps()
    # print(json_data)

    # taskId = '732411b8-dded-40b0-a8d3-ca501bd21267'

    # # list missions and parse json
    # json_data = rmapi.list_missions()
    # print(json_data)

    # list_data = json_data['result']['list']

    # print(list_data[0]['status'])
    # res = rmapi.get_latest_mission_status()
    # print(res)
    # # get mission status
    # for i in range(len(list_data)):
    #     print(list_data[i]['status'])
    
    # # # get Mission(Job or Mission)
    # # for i in range(len(list_data)):
    # #     if(list_data[i]['type'] == 2):
    # #         print(list_data[i])

