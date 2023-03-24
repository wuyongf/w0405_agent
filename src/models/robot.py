import time
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
import src.models.mqtt_rv as RVMQTT
import src.models.api_rm as RMAPI
import src.models.db_robot as RobotDB
import src.models.trans_rvrm as Trans
import src.models.schema_rm as RMSchema

class Robot:
    def __init__(self, config):
        self.rvapi = RVAPI.RVAPI(config)
        self.rvmqtt = RVMQTT.RVMQTT(config)
        self.rmapi = RMAPI.RMAPI(config)
        self.nwdb = RobotDB.robotDBHandler(config)
        self.T = Trans.RVRMTransform()

        self.rvmqtt.start()

    def localize(self, task_json):
        try:
            # step 1. parse task json
            # print('step 1')
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            rv_map_name = self.nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = self.rvapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            # print('step 2')
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x, rv_map_metadata.y, rv_map_metadata.angle)
            rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x, rm_map_metadata.y, rm_map_metadata.heading)
            # step 3. rv. create point base on rm. localization.
            # print('step 3')
            self.rvapi.delete_all_waypoints(rv_map_name)
            self.rvapi.post_new_waypoint(rv_waypoint.mapName, rv_waypoint.name, rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            self.rvapi.change_mode_navigation()
            self.rvapi.change_map(rv_map_name)
            self.rvapi.update_initial_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            # step 4. double check
            # print('step 4')
            pose_is_valid = True
            # pose_is_valid = self.rvapi.check_current_pose_valid()
            map_is_active = self.rvapi.get_active_map().name == rv_map_name
            if(pose_is_valid & map_is_active): return True
            else: return False
        except:
            return False
        
    def goto(self, task_json):
        try:
            # step 1. get rm_map_id, rv_map_name, map_metadata
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            rv_map_name = self.nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = self.rvapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x, rv_map_metadata.y, rv_map_metadata.angle)
            rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x, rm_map_metadata.y, rm_map_metadata.heading)
            # step3. rv. create point base on rm. localization.
            self.rvapi.post_navigation_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            # check if it has arrived
            while(self.rvapi.get_navigation_result() is None): time.sleep(1)
            # step 4. double check
            navigation_is_succeeded = self.rvapi.get_navigation_result()['status'] == 'SUCCEEDED'
            pose_is_valid = self.rvapi.check_current_pose_valid()
            map_is_active = self.rvapi.get_active_map().name == rv_map_name
            if(navigation_is_succeeded & pose_is_valid & map_is_active): return True
            else: return False
        except: return False

    def led_on(self, task: RMSchema.Task):
        try: 
            self.rvapi.set_led_status(on = 1)
            return True
        except: return False
        
    def led_off(self, task: RMSchema.Task):
        try: 
            self.rvapi.set_led_status(on = 0)
            return True
        except: return False

    def get_current_pose(self):
        ## 1. get rv current map/ get rv activated map
        map_json= self.rvapi.get_active_map_json()
        rv_map_metadata = self.rvapi.get_map_metadata(map_json['name'])
        # map_json = None # FOR DEBUG/TESTING
        ## 2. update T params
        if (rv_map_metadata is not None):
            # print(map_json['name'])
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x, rv_map_metadata.y, rv_map_metadata.angle)
        else:
            self.T.clear_rv_map_info()
            print(f'[robot.get_curent_pos()] Warning: Please activate map first, otherwise the pose is not correct.')
            return 0.0, 0.0, 0.0
        ## 3. transfrom
        # pos = self.rvapi.get_current_pose()
        # return self.T.waypoint_rv2rm(pos.x, pos.y, pos.angle)
        pos = self.rvmqtt.get_current_pose()
        return self.T.waypoint_rv2rm(pos[0], pos[1], pos[2])
    
    def get_current_map_rm_guid(self):
        # 1. get rv_current map
        rv_map_name = self.rvapi.get_active_map().name
        # 2. check nwdb. check if there is any map related to rv_current map
        map_is_exist = self.nwdb.check_map_exist(rv_map_name)
        # 3. if yes, get rm_guid. if no, return default idle_guid
        if(map_is_exist):
            return self.nwdb.get_map_rm_guid(rv_map_name)
        else: return '00000000-0000-0000-0000-000000000000'

    def get_current_map_id(self):
        # 1. get rv_current map
        rv_map_name = self.rvapi.get_active_map().name
        # 2. check nwdb. check if there is any map related to rv_current map
        map_is_exist = self.nwdb.check_map_exist(rv_map_name)
        # 3. if yes, get rm_guid. if no, return default idle_guid
        if(map_is_exist):
            return self.nwdb.get_map_id(rv_map_name)
        else: return None
    
    def get_status(self):
        pass

    def get_battery_state(self):
        battery = self.rvapi.get_battery_state().percentage
        return round(battery * 100, 3)


if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    robot = Robot(config)
    while(True):
        time.sleep(1)
        print(robot.get_current_map_rm_guid())