import time
import threading 
import logging
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
import src.models.mqtt_rv as RVMQTT
import src.models.mqtt_rv2 as RVMQTT2
import src.models.api_rm as RMAPI
import src.models.db_robot as RobotDB
import src.models.trans_rvrm as Trans
import src.models.schema_rm as RMSchema
import src.models.enums_rm as RMEnum

class Robot:
    def __init__(self, config):
        self.rvapi = RVAPI.RVAPI(config)
        self.rvmqtt = RVMQTT2.RVMQTT(config)
        # self.rmapi = RMAPI.RMAPI(config)
        self.nwdb = RobotDB.robotDBHandler(config)
        self.T = Trans.RVRMTransform()
        # self.rvmqtt.start() # for RVMQTT.RVMQTT

        # nw sensors
        self.iaq_sensor = ''
        self.laser_sensor = ''
        self.phone = ''

        ## robot baisc info
        self.connection_status = 0
        self.mission_status = 0

    # robot status
    def get_battery_state(self):
        battery = self.rvmqtt.get_battery_percentage()
        # battery = self.rvapi.get_battery_state().percentage
        return round(battery * 100, 3)

    def get_current_pose(self):
        try:
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
        except:
            return 0,0,0

    def get_current_map_rm_guid(self):
        try:
            # 1. get rv_current map
            rv_map_name = self.rvapi.get_active_map().name
            # 2. check nwdb. check if there is any map related to rv_current map
            map_is_exist = self.nwdb.check_map_exist(rv_map_name)
            # 3. if yes, get rm_guid. if no, return default idle_guid
            if(map_is_exist):
                return self.nwdb.get_map_rm_guid(rv_map_name)
            else: return '00000000-0000-0000-0000-000000000000'
        except:
            return '00000000-0000-0000-0000-000000000000'

    def get_current_mapPose(self):
        pixel_x, pixel_y, heading = self.get_current_pose()
        mapId = self.get_current_map_rm_guid()
        return RMSchema.mapPose(mapId, pixel_x, pixel_y, heading)
        
    def get_current_map_id(self):
        try:
            # 1. get rv_current map
            rv_map_name = self.rvapi.get_active_map().name
            # 2. check nwdb. check if there is any map related to rv_current map
            map_is_exist = self.nwdb.check_map_exist(rv_map_name)
            # 3. if yes, get rm_guid. if no, return default idle_guid
            if(map_is_exist):
                return self.nwdb.get_map_id(rv_map_name)
            else: return None
        except:
            return None
    
    # basic robot control
    def cancel_current_task(self):
        self.rvapi.delete_current_task() # rv
        return
    
    def pause_current_task(self):
        self.rvapi.pause_robot_task() # rv
        return
    
    def resume_current_task(self):
        self.rvapi.resume_robot_task() #rv
        pass

    # robot skills
    def localize(self, task_json):
        try:
            # step 0. init. clear current task
            self.cancel_current_task()
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
        
    def goto(self, task_json, status_callback):
        try:
            # step 0. init. clear current task
            self.cancel_current_task()
            # step 1. get rm_map_id, rv_map_name, map_metadata
            # print('step1')
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            rv_map_name = self.nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = self.rvapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            # print('step2')
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x, rv_map_metadata.y, rv_map_metadata.angle)
            rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x, rm_map_metadata.y, rm_map_metadata.heading)
            # step3. rv. create point base on rm. localization.
            # method 1: navigation
            # self.rvapi.post_navigation_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            # while(self.rvapi.get_navigation_result() is None): time.sleep(1) # check if it has arrived
            # # method 2: single task contains a point 'temp'
            # print('step3')
            self.rvapi.delete_all_waypoints(rv_map_name)
            pose_name = 'temp'
            self.rvapi.post_new_waypoint(rv_map_name, pose_name, rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            self.rvapi.post_new_navigation_task(pose_name, orientationIgnored=True)

            thread = threading.Thread(target=self.thread_check_mission_status, args=(task_json, status_callback))
            thread.setDaemon(True)
            thread.start()

            return True
        except: return False

    def thread_check_mission_status(self, task_json, status_callback):
        logging.debug('[check_mission_status] Starting...')
        rm_task_data = RMSchema.Task(task_json)
        continue_flag = True
        while(continue_flag):
            time.sleep(2)
            if(self.rvapi.get_robot_is_moving()):
                print('is moving...')
                time.sleep(1)
                continue
            else:
                continue_flag = False
                time.sleep(1)
                # check if arrive, callback
                if(self.check_goto_has_arrived()): 
                    print('flag arrive')
                    status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Complete)
                # if error
                if(self.check_goto_has_error): 
                    print('flag error') # throw error log
                    status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Fail)
                # if cancelled
                if(self.check_goto_is_cancelled()): 
                    print('flag cancelled')
        logging.debug('[check_mission_status] Exiting...')

    def check_goto_has_arrived(self):
        return self.rvapi.get_task_is_completed()
    
    def check_goto_is_cancelled(self):
        return self.rvapi.get_task_is_cancelled()
    
    def check_goto_has_error(self):
        return self.rvapi.get_task_has_exception()
    
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
   
    def get_mission_status(self):
        pass 

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    robot = Robot(config)

    def status_callback(): pass
    json_data = {}

    print(robot.get_battery_state())
    
    # while(True):
    #     time.sleep(1)
    #     print(robot.get_current_map_rm_guid())