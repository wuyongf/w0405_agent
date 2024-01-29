# sys
import time, os
from pathlib import Path
import threading
from multiprocessing import Process, shared_memory
import datetime
import logging
import uuid
import json
# nwsys
import src.utils.methods as umethods
# import src.models.api_rv as RVAPI
import src_mir.models.api_mir as MiRAPI
# import src.models.mqtt_rv as RVMQTT
# from src.models.mqtt_rv_joystick import RVJoyStick
import src.models.api_rm as RMAPI
from src.models.mqtt_nw import NWMQTT
from src.models.mqtt_nw_publisher import NWMQTTPub
from src.models.mqtt_emsd_lift import EMSDLift
from src.models.db_robot import robotDBHandler
import src.models.trans as Trans
from src.publishers.pub_mission import MissionPublisher
# Schema
import src.models.schema.rm as RMSchema
import src.models.schema.nw as NWSchema
# import src.models.schema.rv as RVSchema
# Enum
import src.models.enums.rm as RMEnum
import src.models.enums.nw as NWEnum
import src.models.enums.azure as AzureEnum
# # top module
# import src.top_module.db_top_module as TopModuleDB
# import src.top_module.enums.enums_module_status as MoEnum
# from src.top_module.module.lift_levelling_module import LiftLevellingModule
# from src.top_module.module.iaqV2 import IaqSensor
# from src.top_module.module.locker import Locker
# from src.top_module.module.access_control_module import AccessControl
# from src.top_module.sensor.gyro import Gyro as MoGyro
# # AI
import numpy as np
# from src.handlers.ai_audio_handler import AudioAgent
# from src.handlers.azure_blob_handler import AzureBlobHandler
# from src.handlers.ai_rgbcam_handler import RGBCamAgent
# from src.handlers.ai_thermalcam_handler import ThermalCamAgent
# Notification
from src.handlers.event_handler import EventHandler

class Robot:
    def __init__(self, config, port_config, skill_config_dir, ai_config):
        self.mirapi = MiRAPI.MiRAPI(config)
        # self.rvmqtt = RVMQTT.RVMQTT(config)
        # self.rvjoystick = RVJoyStick(config)
        self.rmapi = RMAPI.RMAPI(config, skill_config_dir)
        # self.nwmqtt = NWMQTT(config, port_config)
        # self.nwmqttpub = NWMQTTPub(config)
        self.nwdb = robotDBHandler(config)
        # self.modb = TopModuleDB.TopModuleDBHandler(config, self.status_summary)
        self.T = Trans.RVRMTransform()
        self.T_RM = Trans.RMLayoutMapTransform()
        self.missionpub = MissionPublisher(skill_config_dir, self.rmapi)

        ## Notification
        self.event_handler = EventHandler("localhost", self.status_summary)
        self.event_handler.start()

        #
        self.config = config
        self.port_config = port_config
        # # self.rvmqtt.start() # for RVMQTT.RVMQTT
        # self.nwmqtt.start()   
        # self.nwmqttpub.start()

        ## robot baisc info
        self.ipc_ip_addr = config.get('IPC', 'localhost')
        self.surface_ip_addr = config.get('SURFACE', 'localhost')
        self.robot_nw_id = self.nwdb.robot_id
        self.robot_rm_guid = self.nwdb.robot_rm_guid
        self.status = RMSchema.Status(0.0, 2, RMSchema.mapPose(), RMSchema.layoutPose())
        self.map_nw_id = None
        self.layout_nw_id = None
        self.layout_rm_guid = None

        ## robot status (mission)
        self.mode =  NWEnum.RobotStatusMode.IDLE
        self.task_status = NWEnum.TaskStatus.NULL
        self.is_charging = False
        self.is_moving = False
        self.has_arrived = False
        self.is_manual_control = False
        self.is_followme = False

        self.a_delivery_mission = None
        
        ## ROBOT CONFIGURATION
        self.skill_config = self.rmapi.skill_config

        ## delivery related
        self.nw_goto_done = False

        ## lift related
        self.last_goto_json = None
        self.lift_task_json = None       
        
        ## nw-door-agent
        self.door_agent_start = False
        self.door_agent_finish = False
        self.door_configured = False

        ## ai related
        self.lnd_mission_id     = None
        self.lnd_wav_file_name  = None
        self.wld_mission_id     = None
        self.wld_image_folder_dir = None

        ## shared memory
        temp_arr = np.zeros(3, dtype=np.float32)
        self.shm = shared_memory.SharedMemory(create=True, size=temp_arr.nbytes)
        self.robot_position = np.ndarray(temp_arr.shape, dtype=temp_arr.dtype, buffer=self.shm.buf) # [layout_id, robot_x, robot_y]
        self.robot_position[:] = temp_arr[:]

    def init(self):
        print(f'[robot.init]: Start...')
        # self.rvapi.wait_for_ready()
        # self.rvapi.put_safety_zone_minimum()
        # self.rvapi.change_mode_navigation()
        # self.rvapi.put_maximum_speed(0.3)
        print(f'[robot.init]: Finish...')
        pass

    def status_start(self):
        threading.Thread(target=self.thread_update_status, args=()).start()  # from RV API
        # threading.Thread(target=self.thread_update_position).start()  # from RV API
        print(f'[robot.status_start]: Start...')

    # def thread_update_position(self):
    #     while True:
    #         # layout
    #         # self.layout_nw_id = self.get_current_layout_nw_id()
    #         layout_x,  layout_y,  layout_heading = self.get_current_layout_pose() # update self.layout_rm_guid also
    #         self.status.layoutPose.x = layout_x
    #         self.status.layoutPose.y = layout_y
    #         self.status.layoutPose.heading = layout_heading
    #         self.robot_position[:] = np.array([self.layout_nw_id, layout_x, layout_y], dtype=np.float32)[:]

    #         time.sleep(0.1)
    
    def thread_update_status(self):  # update thread
        while True:
            try:
                # # # rm status <--- rv status
                # self.status.state = 1  # todo: robot status
                self.status.mapPose.mapId = 'a71042e0-0d2a-4535-bfd8-a18b449e8676'#self.get_current_map_rm_guid()  # map

                status = self.mirapi.get_status()
                self.status.batteryPct = status.percentage
                pixel_x, pixel_y, heading = status.position.x, status.position.y, status.position.orientation

                # print(pixel_x, pixel_y, heading)
                self.status.mapPose.x = pixel_x
                self.status.mapPose.y = pixel_y
                self.status.mapPose.heading = 0#heading

                self.status.layoutPose.x = self.status.mapPose.x
                self.status.layoutPose.y = self.status.mapPose.y
                self.status.layoutPose.heading = self.status.mapPose.heading
                self.robot_position[:] = np.array([self.layout_nw_id, pixel_x, pixel_y], dtype=np.float32)[:]

                # ## To NWDB
                # self.map_nw_id = self.get_current_map_nw_id()

                # ## Mode
                # self.get_current_mode()
                # # self.rvapi.get_robot_is_moving()

                ## Summary
                print(f'-------------------------------------------------------------------')
                # print(f'robot_status.robot_nw_id:    {self.robot_nw_id}')
                # print(f'robot_status.robot_rm_guid:  {self.robot_rm_guid}')
                print(f'robot_status.battery:        {self.status.batteryPct}')
                print(f'robot_status.map_rm_guid:    {self.status.mapPose.mapId}')
                print(f'robot_status.map_rm_pose:    {pixel_x, pixel_y, self.status.mapPose.heading }')
                # print(f'robot_status.layout_nw_id:   {self.layout_nw_id}')
                # print(f'robot_status.layout_rm_guid: {self.layout_rm_guid}')
                # print(f'robot_status.layout_rm_pose: {self.status.layoutPose.x, self.status.layoutPose.y, self.status.layoutPose.heading}')
                # print(f'robot_status.mode:           {self.mode}')
                print(f'-------------------------------------------------------------------')
            except:
                print('[robot.update_status] error!')

            time.sleep(1.0)

    def status_summary(self):
        # 1) init
        protocal = NWEnum.Protocol.RVAPI

        # 2) get status
        # battery = self.get_battery_state(protocal)
        # x, y, theta = self.get_current_pose(protocal)
        # map_id = self.get_current_map_id()
        battery = self.status.batteryPct

        # layout position (x,y,theta)
        x = self.status.layoutPose.x
        y = self.status.layoutPose.y
        theta = self.status.layoutPose.heading

        # # map position
        # map_x = self.robot_status.mapPose.x
        # map_y = self.robot_status.mapPose.y
        # map_theta = self.robot_status.mapPose.heading

        map_id = self.map_nw_id
        map_rm_guid = self.get_current_map_rm_guid()

        # 3) convert to json
        pos = NWSchema.Position(x, y, theta)
        status = NWSchema.Status(battery, pos, map_id, map_rm_guid)
        return status.to_json()

    # robot status
    def get_battery_state(self):
        pass

    def get_current_pose(self, protocol=NWEnum.Protocol):
        try:
            ## 1. get rv current map/ get rv activated map
            map_json = self.mirapi.get_active_map_json()
            rv_map_metadata = self.mirapi.get_map_metadata(map_json['name'])
            # map_json = None # FOR DEBUG/TESTING
            ## 2. update T params
            if (rv_map_metadata is not None):
                # print(map_json['name'])
                self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x,
                                          rv_map_metadata.y, rv_map_metadata.angle)
            else:
                self.T.clear_rv_map_info()
                # print(f'[robot.get_curent_pos()] Warning: Please activate map first, otherwise the pose is not correct.')
                return 0.0, 0.0, 0.0
            ## 3. transfrom
            if (protocol == NWEnum.Protocol.RVMQTT):
                pos = self.rvmqtt.get_current_pose()
                return self.T.waypoint_rv2rm(pos[0], pos[1], pos[2])
            if (protocol == NWEnum.Protocol.RVAPI):
                pos = self.mirapi.get_current_pose()
                return self.T.waypoint_rv2rm(pos.x, pos.y, pos.angle)
        except:
            return 0, 0, 0

    def get_current_layout_pose(self):
        try:

            map_rm_guid = self.status.mapPose.mapId
            self.layout_rm_guid = self.rmapi.get_layout_guid(map_rm_guid)
            # print('<debug>layout_pose 1')
            params = self.rmapi.get_layout_map_list(self.layout_rm_guid, map_rm_guid)
            # print('<debug>layout_pose 2')
            self.T_RM.update_layoutmap_params(params.imageWidth, params.imageHeight, 
                                              params.scale, params.angle, params.translate)
            # print('<debug>layout_pose 3')
            cur_layout_point = self.T_RM.find_cur_layout_point(self.status.mapPose.x, 
                                                               self.status.mapPose.y,
                                                               self.status.mapPose.heading)
            return cur_layout_point
        except:
            return 0, 0, 0

    def get_current_map_rm_guid(self):
        try:
            # 1. get rv_current map
            rv_map_name = self.mirapi.get_active_map().name
            # 2. check nwdb. check if there is any map related to rv_current map
            map_is_exist = self.nwdb.check_map_exist(rv_map_name)
            # 3. if yes, get rm_guid. if no, return default idle_guid
            if (map_is_exist):
                return self.nwdb.get_map_rm_guid(rv_map_name)
            else:
                return '00000000-0000-0000-0000-000000000000'
        except:
            return '00000000-0000-0000-0000-000000000000'

    def get_current_mapPose(self):
        # pixel_x, pixel_y, heading = self.get_current_pose()
        # mapId = self.get_current_map_rm_guid()
        map_id = self.map_nw_id
        x = self.status.mapPose.x
        y = self.status.mapPose.y
        theta = self.status.mapPose.heading
        
        return RMSchema.mapPose(map_id, x, y, theta)

    def get_current_map_nw_id(self):
        try:
            # 1. get rv_current map
            rv_map_name = self.mirapi.get_active_map().name
            # 2. check nwdb. check if there is any map related to rv_current map
            map_is_exist = self.nwdb.check_map_exist(rv_map_name)
            # 3. if yes, get rm_guid. if no, return default idle_guid
            if (map_is_exist):
                return self.nwdb.get_map_id(rv_map_name)
            else:
                return None
        except:
            return None

    def get_current_layout_nw_id(self):
        try:
            map_id = self.get_current_map_nw_id()
            if map_id is None: return None
            layout_id = self.nwdb.get_single_value('robot.map.layout', 'ID', 'activated_map_id', map_id)
            return layout_id

        except:
            return None

    def get_current_mode(self):

        # E-Stop
        if(self.mirapi.get_status_estop()): 
            self.mode = NWEnum.RobotStatusMode.ESTOP
            return
        
        # Charging
        if(self.is_charging):
            self.mode = NWEnum.RobotStatusMode.CHARGING
            return
        
        # Manual Control
        if(self.is_manual_control):
            self.mode = NWEnum.RobotStatusMode.MANUAL
            return
        
        # FollowME
        if(self.is_followme):
            self.mode = NWEnum.RobotStatusMode.FOLLOWME
            return

        # Executing
        if(self.task_status == NWEnum.TaskStatus.EXECUTING or self.is_moving): 
            self.mode = NWEnum.RobotStatusMode.EXECUTING
            return

        # IDEL
        if((self.task_status == NWEnum.TaskStatus.NULL) and (self.is_moving == False)):
            self.mode = NWEnum.RobotStatusMode.IDLE
            return

    # basic robot control
    def cancel_moving_task(self):
        self.mirapi.delete_current_task()  # rv
        return

    def pause_robot_task(self):
        self.mirapi.pause_robot_task()  # rv
        return

    def resume_robot_task(self):
        self.mirapi.resume_robot_task()  #rv
        pass

    # robot skills
    def localize(self, task_json):
        try:
            print(f'localize: {task_json}')
            # step 0. init. clear current task
            self.cancel_moving_task()
            # step 1. parse task json
            # print('step 1')
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            rv_map_name = self.nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = self.mirapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            # print('step 2')
            map_rm_guid = self.nwdb.get_map_rm_guid(rv_map_name)
            self.layout_rm_guid = self.rmapi.get_layout_guid(map_rm_guid)
            params = self.rmapi.get_layout_map_list(self.layout_rm_guid, map_rm_guid)
            self.T_RM.update_layoutmap_params(params.imageWidth, params.imageHeight, 
                                              params.scale, params.angle, params.translate)
            
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x,
                                      rv_map_metadata.y, rv_map_metadata.angle)            
            rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x,
                                                rm_map_metadata.y, rm_map_metadata.heading - self.T_RM.map_rotate_angle)

            print(f'<heading_debug> rv_map_metadata.angle: {rv_map_metadata.angle}')
            print(f'<heading_debug> self.T_RM.map_rotate_angle: {self.T_RM.map_rotate_angle}')
            # step 3. rv. create point base on rm. localization.
            # print('step 3')
            self.mirapi.delete_all_waypoints(rv_map_name)
            self.mirapi.post_new_waypoint(rv_waypoint.mapName, rv_waypoint.name, rv_waypoint.x, rv_waypoint.y,
                                         rv_waypoint.angle)
            self.mirapi.change_mode_navigation()
            self.mirapi.change_map2(rv_map_name, rv_waypoint.name)
            self.mirapi.update_initial_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            print(f'[aaa] init_heading: {rv_waypoint.angle}' )
            # step 4. double check
            # print('step 4')
            pose_is_valid = True
            # pose_is_valid = self.rvapi.check_current_pose_valid()
            map_is_active = self.mirapi.get_active_map().name == rv_map_name
            if (pose_is_valid & map_is_active): 
                # self.nwdb.update_robot_status_mode(NWEnum.RobotStatusMode.IDLE)
                return True
            else: return False
        except:
            return False

    def goto(self, task_json, status_callback):
        '''
        No TMat Transformation!!! Just RM_MAP -> RV_MAP
        '''
        try:
            # ## Lift Integration - Rev01
            # if(self.is_another_floor(task_json)):

            #     self.last_goto_json = task_json
            #     # init goto_across_floor
            #     print(f'[robot.goto] init goto_across_floor...')

            #     # cur_layout_id = self.layout_nw_id
            #     # target_map_rm_guid = task_json['parameters']['mapId']
            #     # target_layout_id = self.nwdb.get_single_value('robot.map', 'layout_id', 'rm_guid', target_map_rm_guid)
            #     # self.get_lift_mission_detail(cur_layout_id, target_layout_id)
            #     rm_task_data = RMSchema.Task(task_json)
            #     status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Completed)
            #     time.sleep(1)

                
            #     threading.Thread(target=self.lift_mission_publisher).start()
            #     return True
            # self.rvapi.put_safety_zone_minimum()
            # self.rvapi.put_maximum_speed(0.3)

            self.mirapi.put_safety_zone_minimum()
            self.mirapi.put_maximum_speed(0.3)

            self.door_configured = False
            self.door_agent_start = True  # door-agent logic
            self.door_agent_finish = False
            while( not self.door_configured): time.sleep(1)
            print(f'[goto] door configuredd!')

            # step 0. init. clear current task
            self.cancel_moving_task()
            # step 1. get rm_map_id, rv_map_name, map_metadata
            # print('step1')
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            rv_map_name = self.nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = self.mirapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            # print('step2')
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x,
                                      rv_map_metadata.y, rv_map_metadata.angle)
            # rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x,
            #                                     rm_map_metadata.y, rm_map_metadata.heading - self.T_RM.map_rotate_angle)  ## 0
            rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x,
                                                rm_map_metadata.y, rm_map_metadata.heading )  ## 271
            # step3. rv. create point base on rm. localization.
            # print('step3')
            self.mirapi.delete_all_waypoints(rv_map_name)
            pose_name = 'TEMP'
            time.sleep(1)
            print(f'goto--rm_map_x: {rm_map_metadata.x}')
            print(f'goto--rm_map_y: {rm_map_metadata.y}')
            print(f'goto--rm_map_heading: {rm_map_metadata.heading}')
            self.mirapi.post_new_waypoint(rv_map_name, pose_name, rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            time.sleep(1)
            self.mirapi.post_new_navigation_task(pose_name, orientationIgnored=False)

            thread = threading.Thread(target=self.thread_check_mission_status, args=(task_json, status_callback))
            thread.setDaemon(True)
            thread.start()

            return True
        except:
            return False
      
    def rmove(self, task_json):
        try:
            param = task_json['parameters']

            print(param)

            self.mirapi.rmove_demo()

            return True
        except:
            return False

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    skill_config_path = '../../conf/rm_skill.properties'
    ai_config = umethods.load_config('../ai_module/lift_noise/cfg/config.properties')

    robot = Robot(config, port_config, skill_config_path, ai_config)
    robot.status_start()


    
