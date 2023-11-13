import time
import threading
import logging
import uuid
import json
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
import src.models.mqtt_rv as RVMQTT
from src.models.mqtt_rv_joystick import RVJoyStick
import src.models.api_rm as RMAPI
from src.models.mqtt_nw import NWMQTT
from src.models.mqtt_nw_publisher import NWMQTTPub
from src.models.mqtt_emsd_lift import EMSDLift

import src.models.db_robot as RobotDB
import src.top_module.db_top_module as TopModuleDB
import src.models.trans as Trans
# Schema
import src.models.schema.rm as RMSchema
import src.models.schema.nw as NWSchema
import src.models.schema.rv as RVSchema
# Enum
import src.models.enums.rm as RMEnum
import src.models.enums.nw as NWEnum
# top module
import src.top_module.enums.enums_module_status as MoEnum
from src.top_module.module.lift_levelling_module import LiftLevellingModule
# from src.top_module.module.iaq import IaqSensor
from src.top_module.module.iaqV2 import IaqSensor
from src.top_module.module.locker import Locker
from src.top_module.module.access_control_module import AccessControl
from src.top_module.sensor.gyro import Gyro as MoGyro


class Robot:
    def __init__(self, config, port_config, skill_config_path):
        self.rvapi = RVAPI.RVAPI(config)
        self.rvmqtt = RVMQTT.RVMQTT(config)
        self.rvjoystick = RVJoyStick(config)
        self.rmapi = RMAPI.RMAPI(config)
        self.nwmqtt = NWMQTT(config, port_config)
        self.nwmqttpub = NWMQTTPub(config)
        self.emsdlift = EMSDLift(config)
        self.nwdb = RobotDB.robotDBHandler(config)
        self.modb = TopModuleDB.TopModuleDBHandler(config, self.status_summary)
        self.T = Trans.RVRMTransform()
        self.T_RM = Trans.RMLayoutMapTransform()
        self.config = config
        self.port_config = port_config
        # self.rvmqtt.start() # for RVMQTT.RVMQTT
        self.nwmqtt.start()   
        self.nwmqttpub.start()
        
        # self.module_lift_inspect =Modules.LiftInspectionSensor()
        # self.module_internal = Modules.InternalDevice()
        # self.module_monitor = Modules.Monitor()
        # self.modmodule_phone = Modules.PhoneDevice()

        ## robot baisc info
        self.ipc_ip_addr = config.get('IPC', 'localhost')
        self.surface_ip_addr = config.get('SURFACE', 'localhost')
        self.robot_nw_id = self.nwdb.robot_id
        self.robot_rm_guid = self.nwdb.robot_guid
        self.status = RMSchema.Status(0.0, 0, RMSchema.mapPose(), RMSchema.layoutPose())
        self.map_nw_id = None
        self.layout_nw_id = None
        self.layout_rm_guid = None

        self.a_delivery_mission = None
        self.robot_locker_is_closed = self.locker_is_closed()

        # # # module - models/sensors
        self.mo_lift_levelling = LiftLevellingModule(self.modb, config, port_config, self.status_summary)
        self.mo_iaq = IaqSensor(self.modb, config, port_config, self.status_summary, Ti=1)
        self.mo_locker = Locker(port_config)
        self.mo_access_control = AccessControl(self.modb, config, port_config)
        self.mo_gyro = MoGyro(self.modb, config, port_config, self.status_summary)
        
        ## delivery related
        #region ROBOT CONFIGURATION
        self.rmapi.write_robot_skill_to_properties(self.robot_rm_guid, skill_config_path)
        # print(f'[new_delivery_mission]: write Robot Skill...')
        self.skill_config = umethods.load_config(skill_config_path)
        # print(f'[new_delivery_mission]: Loaded Robot Skill...')
        #endregion

        ## lift related
        self.last_goto_json = None
        
        ## nw-door-agent
        self.door_agent_start = False
        self.door_agent_finish = False

    def sensor_start(self):
        self.mo_iaq.start()
        self.nwmqttpub.fans_off("all")
        self.nwmqttpub.rotate_camera(90)

        # delivery
        self.nwdb.update_single_value('ui.display.status','ui_flag',0,'robot_id',self.robot_nw_id)

        # lift
        self.emsdlift.start()

        # self.mo_access_control.start()
        print(f'[robot.sensor_start]: Start...')

    def init(self):
        print(f'[robot.init]: Start...')
        self.rvapi.wait_for_ready()
        self.rvapi.put_safety_zone_minimum()
        self.rvapi.change_mode_navigation()
        self.rvapi.put_maximum_speed(0.3)
        print(f'[robot.init]: Finish...')
        pass

    def status_start(self, protocol: NWEnum.Protocol):
        threading.Thread(target=self.update_status, args=(protocol, )).start()  # from RV API
        print(f'[robot.status_start]: Start...')

    def update_status(self, protocol):  # update thread
        while True:
            try:
                # # rm status <--- rv status
                self.status.state = 1  # todo: robot status
                self.status.mapPose.mapId = self.get_current_map_rm_guid()  # map
                self.status.batteryPct = self.get_battery_state(protocol)  # battery
                pixel_x, pixel_y, heading = self.get_current_pose(protocol)  # current map pose
                # print(pixel_x, pixel_y, heading)
                self.status.mapPose.x = pixel_x
                self.status.mapPose.y = pixel_y
                self.status.mapPose.heading = heading

                # layout
                self.layout_nw_id = self.get_current_layout_nw_id()
                layout_x,  layout_y,  layout_heading = self.get_current_layout_pose() # update self.layout_rm_guid also
                self.status.layoutPose.x = layout_x
                self.status.layoutPose.y = layout_y
                self.status.layoutPose.heading = layout_heading
                # Modules
                self.robot_locker_is_closed = self.locker_is_closed()

                ## TO NWDB
                self.map_nw_id = self.get_current_map_nw_id()

                ## Summary
                print(f'robot_nw_id: {self.robot_nw_id}')
                print(f'robot_rm_guid: {self.robot_rm_guid}')
                print(f'robot_status.battery: {self.status.batteryPct}')
                print(f'robot_status.map_rm_guid: {self.status.mapPose.mapId}')
                print(f'robot_status.map_rm_pose: ({pixel_x, pixel_y, heading})')
                print(f'robot_status.layout_nw_id: {self.layout_nw_id}')
                print(f'robot_status.layout_rm_guid: {self.layout_rm_guid}')
                print(f'robot_status.layout_rm_pose: ({layout_x, layout_y, layout_heading})')
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
    def get_battery_state(self, protocol=NWEnum.Protocol):
        if (protocol == NWEnum.Protocol.RVMQTT):
            battery = self.rvmqtt.get_battery_percentage()
        if (protocol == NWEnum.Protocol.RVAPI):
            battery = self.rvapi.get_battery_state().percentage
        return round(battery * 100, 3)

    def get_current_pose(self, protocol=NWEnum.Protocol):
        try:
            ## 1. get rv current map/ get rv activated map
            map_json = self.rvapi.get_active_map_json()
            rv_map_metadata = self.rvapi.get_map_metadata(map_json['name'])
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
                pos = self.rvapi.get_current_pose()
                return self.T.waypoint_rv2rm(pos.x, pos.y, pos.angle)
        except:
            return 0, 0, 0

    def get_current_layout_pose(self):
        try:

            map_rm_guid = self.status.mapPose.mapId
            self.layout_rm_guid = self.rmapi.get_layout_guid(map_rm_guid)
            print('<debug>layout_pose 1')
            params = self.rmapi.get_layout_map_list(self.layout_rm_guid, map_rm_guid)
            print('<debug>layout_pose 2')
            self.T_RM.update_layoutmap_params(params.imageWidth, params.imageHeight, 
                                              params.scale, params.angle, params.translate)
            print('<debug>layout_pose 3')
            cur_layout_point = self.T_RM.find_cur_layout_point(self.status.mapPose.x, 
                                                               self.status.mapPose.y,
                                                               self.status.mapPose.heading)
            return cur_layout_point
        except:
            return 0, 0, 0

    def get_current_map_rm_guid(self):
        try:
            # 1. get rv_current map
            rv_map_name = self.rvapi.get_active_map().name
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
            rv_map_name = self.rvapi.get_active_map().name
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

    # basic robot control
    def cancel_moving_task(self):
        self.rvapi.delete_current_task()  # rv
        return

    def pause_robot_task(self):
        self.rvapi.pause_robot_task()  # rv
        return

    def resume_robot_task(self):
        self.rvapi.resume_robot_task()  #rv
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
            rv_map_metadata = self.rvapi.get_map_metadata(rv_map_name)
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
            self.rvapi.delete_all_waypoints(rv_map_name)
            self.rvapi.post_new_waypoint(rv_waypoint.mapName, rv_waypoint.name, rv_waypoint.x, rv_waypoint.y,
                                         rv_waypoint.angle)
            self.rvapi.change_mode_navigation()
            self.rvapi.change_map2(rv_map_name, rv_waypoint.name)
            self.rvapi.update_initial_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            print(f'[aaa] init_heading: {rv_waypoint.angle}' )
            # step 4. double check
            # print('step 4')
            pose_is_valid = True
            # pose_is_valid = self.rvapi.check_current_pose_valid()
            map_is_active = self.rvapi.get_active_map().name == rv_map_name
            if (pose_is_valid & map_is_active): 
                self.nwdb.update_robot_status_mode(NWEnum.RobotStatusMode.Auto)
                return True
            else: return False
        except:
            return False

    def is_another_floor(self, task_json):
        # target_map_metadata = RMSchema.TaskParams(task_json['parameters'])
        target_map_id = task_json['parameters']['mapId']
        if(self.status.mapPose.mapId != target_map_id): return True
        return False

    # status_callback: check task_handler3.py
    def goto(self, task_json, status_callback):
        '''
        No TMat Transformation!!! Just RM_MAP -> RV_MAP
        '''
        try:
            if(self.is_another_floor(task_json)):

                self.last_goto_json = task_json
                # init goto_across_floor
                print(f'[robot.goto] init goto_across_floor...')

                # cur_layout_id = self.layout_nw_id
                # target_map_rm_guid = task_json['parameters']['mapId']
                # target_layout_id = self.nwdb.get_single_value('robot.map', 'layout_id', 'rm_guid', target_map_rm_guid)
                # self.get_lift_mission_detail(cur_layout_id, target_layout_id)
                rm_task_data = RMSchema.Task(task_json)
                status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Completed)
                time.sleep(1)

                
                threading.Thread(target=self.lift_mission_publisher).start()
                return True

            self.door_agent_start = True  # door-agent logic
            self.door_agent_finish = False
            time.sleep(1)

            # step 0. init. clear current task
            self.cancel_moving_task()
            # step 1. get rm_map_id, rv_map_name, map_metadata
            # print('step1')
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            rv_map_name = self.nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = self.rvapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            # print('step2')
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x,
                                      rv_map_metadata.y, rv_map_metadata.angle)
            rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x,
                                                rm_map_metadata.y, rm_map_metadata.heading - self.T_RM.map_rotate_angle)
            # step3. rv. create point base on rm. localization.
            # print('step3')
            self.rvapi.delete_all_waypoints(rv_map_name)
            pose_name = 'TEMP'
            time.sleep(1)
            print(f'goto--rm_map_x: {rm_map_metadata.x}')
            print(f'goto--rm_map_y: {rm_map_metadata.y}')
            print(f'goto--rm_map_heading: {rm_map_metadata.heading}')
            self.rvapi.post_new_waypoint(rv_map_name, pose_name, rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            time.sleep(1)
            self.rvapi.post_new_navigation_task(pose_name, orientationIgnored=False)

            thread = threading.Thread(target=self.thread_check_mission_status, args=(task_json, status_callback))
            thread.setDaemon(True)
            thread.start()

            return True
        except:
            return False

    def thread_check_charging_status(self, task_json, status_callback):
        print('[charging.check_mission_status] Starting...')
        rm_task_data = RMSchema.Task(task_json)
        continue_flag = True
        while (continue_flag):
            time.sleep(2)
            status = self.rvapi.get_charging_feedback()

            if (status == 'NOT_CHARGING'):
                continue_flag = False
                time.sleep(1)
                status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Completed)

            if (status == 'PRE_CHARGING' or status == 'CHARGING' or status == 'POST_CHARGING'):
                print('[charging.check_mission_status] robot is charging...')
                time.sleep(1)
                continue

        print('[charging.check_mission_status] Exiting...')

    def thread_check_mission_status(self, task_json, status_callback):

        print('[goto.check_mission_status] Starting...')
        rm_task_data = RMSchema.Task(task_json)
        continue_flag = True
        while (continue_flag):
            time.sleep(2)
            if (self.rvapi.get_robot_is_moving()):
                print('[goto.check_mission_status] robot is moving...')
                time.sleep(1)
                continue
            else:
                continue_flag = False
                time.sleep(1)
                # check if arrive, callback
                if (self.check_goto_has_arrived()):
                    print('[goto.check_mission_status] robot has arrived!')
                    status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Completed)

                # # if error
                # if(self.check_goto_has_error):
                #     print('flag error') # throw error log
                #     status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Fail)
                # if cancelled
                if (self.check_goto_is_cancelled()):
                    print('[goto.check_mission_status] robot has cancelled moving task')
                    status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Failed)

                self.door_agent_start = False
                self.door_agent_finish = True  # door-agent logic
        print('[goto.check_mission_status] Exiting...')

    def check_goto_has_arrived(self):
        return self.rvapi.get_task_is_completed()

    def check_goto_is_cancelled(self):
        return self.rvapi.get_task_is_cancelled()

    def check_goto_has_error(self):
        return self.rvapi.get_task_has_exception()

    def led_on(self, task: RMSchema.Task):
        try:
            self.rvapi.set_led_status(on=1)
            return True
        except:
            return False

    def led_off(self, task: RMSchema.Task):
        try:
            self.rvapi.set_led_status(on=0)
            return True
        except:
            return False

    def get_mission_status(self):
        pass

    # Module - IAQ
    def iaq_on(self, task_json):
        try:
            rm_mission_guid = self.rmapi.get_mission_id(task_json)

            self.nwdb.insert_new_mission_id(self.robot_nw_id, rm_mission_guid, NWEnum.MissionType.IAQ)
            mission_id = self.nwdb.get_latest_mission_id()

            # mission_id = self.rmapi.get_mission_id(task_json['taskId'])
            print(f'mission_id: {mission_id}')
            self.mo_iaq.set_task_mode(e=True, task_id=mission_id)
            return True
        except:
            return False

    def iaq_off(self, task_json):
        try:
            self.mo_iaq.set_task_mode(False)
            return True
        except:
            return False


    # Follow Me
    def follow_me_mode(self, task_json):
        try:
            self.rvapi.change_mode_followme()
            # update nwdb robot.status.mode
            self.nwdb.update_robot_status_mode(NWEnum.RobotStatusMode.FollowME_Unpair)
            return True
        except:
            return False

    def follow_me_pair(self, task_json):
        # call pairing api
        self.rvapi.post_followme_pair()
        print('start pairing')
        # wait for a sec
        time.sleep(1)
        count = 0
        # count down when pairing 10s
        while count < 10:
            pairing_state = self.is_paired()
            print(f'pairing state:{pairing_state}')
            time.sleep(1)
            if pairing_state == True:
                print('paired')
                # update nwdb robot.status.mode
                self.nwdb.update_robot_status_mode(NWEnum.RobotStatusMode.FollowME_Paired)
                return True
            elif pairing_state == 'PAIRING':
                count = count + 1
                print(f'pairing, {10-count}s left')
        print("pairing time out")
        return False

    def is_paired(self):
        result = self.rvapi.get_followme_pairing_state()
        # while True:
        #     print(state)
        # state = RVSchema.FollowMe
        if result == "PAIRED":
            print("paired")
            return True
        elif result == "PAIRING":
            print("pairing")
            return result
        elif result == "UNPAIRED":
            print("unpaired")
            return False

    def follow_me_unpair(self, task_json):
        try:
            self.rvapi.post_followme_unpair()
            time.sleep(2)
            if self.is_paired() != True:
                return True
            else:
                return False
        except:
            return False

    # Module - Lift Inspection
    # todo: lift noise/ lift video/ lift height/ lift vibration/ lift levelling

    def lift_vibration_on(self, task_json):
        # try:
        self.mo_gyro = MoGyro(self.modb, self.config, self.port_config, self.status_summary)
        rm_mission_guid = self.rmapi.get_mission_id(task_json)
        self.nwdb.insert_new_mission_id(self.robot_nw_id, rm_mission_guid, NWEnum.MissionType.LiftAcc)
        mission_id = self.nwdb.get_latest_mission_id()

        print(f'mission_id: {mission_id}')

        self.mo_gyro.set_task_id(id=mission_id)
        time.sleep(0.3)
        self.mo_gyro.start()

        return True

    # except: return False

    def lift_vibration_off(self, task_json):
        try:
            self.mo_gyro.stop()
            return True
        except:
            return False

    def inspect_lift_levelling(self, task_json):
        def get_status():
            return self.mo_lift_levelling.get_status()

        # TODO:
        try:
            # Need to create new instance everytime start thread
            # Otherwise will case error [RuntimeError: threads can only be started once]
            self.mo_lift_levelling = LiftLevellingModule(self.modb, self.config, self.port_config, self.status_summary)

            rm_mission_guid = self.rmapi.get_mission_id(task_json)
            self.nwdb.insert_new_mission_id(self.robot_nw_id, rm_mission_guid, NWEnum.MissionType.LiftLevelling)
            mission_id = self.nwdb.get_latest_mission_id()

            self.mo_lift_levelling.set_task_id(id=mission_id)
            self.mo_lift_levelling.start()
            time.sleep(1)

        except:
            return False

        while (get_status() == MoEnum.LiftLevellingStatus.Executing):
            time.sleep(1)

        if (get_status() == MoEnum.LiftLevellingStatus.Finish):
            return True
        else:
            return False

    # Module - Lift Inspection - End

    # LIFT
    # Lift Init
    def get_lift_mission_detail(self, cur_layout_id, target_layout_id):
        self.a_lift_mission = self.nwdb.configure_lift_mission(cur_layout_id, target_layout_id)
        return self.a_lift_mission
    
    # DELIVERY
    # def configure_delivery_mission(self, available_delivery_ID):
    def locker_unlock(self):
        try:
            self.mo_locker.unlock()
            time.sleep(0.2)
            if (self.mo_locker.is_closed() is not True): return True
            return False
        except:
            return False

    def locker_is_closed(self):
        try:
            return self.mo_locker.is_closed()
        except:
            return False

    # Delivery Init
    def get_available_delivery_mission(self):
        try:
            # check available delivery mission
            id = self.nwdb.get_available_delivery_id()
            if id == None:
                print('There is no any available delivery misssion!!')
                return False

            # configure the delivery mission
            # a_delivery_mission: NWSchema
            self.a_delivery_mission = self.nwdb.configure_delivery_mission(available_delivery_id=id)
            return True
        except:
            return False

    def get_delivery_mission_detail(self):
        return self.a_delivery_mission
    
    ## NEW JOB via RMAPI

    def delivery_clear_positions(self, a_delivery_mission: NWSchema.DeliveryMission):
        pos_origin = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_origin_id)
        pos_destination = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_destination_id)
        self.rmapi.delete_all_delivery_markers(layout_id=pos_origin.layout_guid)
        self.rmapi.delete_all_delivery_markers(layout_id=pos_destination.layout_guid)

    # Delivery robot-skill details
    def wait_for_loading_package(self):

        try:
            while True:
                # Check if robot should open the locker.
                locker_command = NWEnum.LockerCommand(self.nwdb.get_locker_command(self.a_delivery_mission.ID))
                if (locker_command == NWEnum.LockerCommand.Unlock):
                    self.locker_unlock()
                    self.nwdb.update_locker_command(NWEnum.LockerCommand.Null.value, self.a_delivery_mission.ID)

                # Check if the job is done (replace with your own condition)
                delivery_status = NWEnum.DeliveryStatus(self.nwdb.get_delivery_status(self.a_delivery_mission.ID))
                if (delivery_status == NWEnum.DeliveryStatus.Active_ToReceiver):
                    return True

                # Wait for a short interval before checking again
                time.sleep(0.5)
        except:
            return False

    def wait_for_unloading_package(self):
        try:
            while True:
                # Check if robot should open the locker.
                locker_command = NWEnum.LockerCommand(self.nwdb.get_locker_command(self.a_delivery_mission.ID))
                if (locker_command == NWEnum.LockerCommand.Unlock):
                    self.locker_unlock()
                    self.nwdb.update_locker_command(NWEnum.LockerCommand.Null.value, self.a_delivery_mission.ID)

                # Check if the job is done (replace with your own condition)
                delivery_status = NWEnum.DeliveryStatus(self.nwdb.get_delivery_status(self.a_delivery_mission.ID))
                if (delivery_status == NWEnum.DeliveryStatus.Active_BackToChargingStation
                        or delivery_status == NWEnum.DeliveryStatus.Active_BackToSender):
                    return True

                # Wait for a short interval before checking again
                time.sleep(0.5)
        except:
            return False
    
    ## Delivery Publisher Methods
    def wait_for_job_done(self, duration_min):
        print(f'[robot.wait_for_job_done]: duration: {duration_min} minutes')
        start_time = time.time()
        time.sleep(0.5)
        while True:
            # Check if the job is done (replace with your own condition)
            if self.rmapi.get_latest_mission_status() == RMEnum.MissionStatus.Completed or self.rmapi.get_latest_mission_status() == RMEnum.MissionStatus.Aborted:
                return True

            # Check if the specified duration has elapsed
            elapsed_time = time.time() - start_time
            if elapsed_time >= (duration_min * 60):  # Convert minutes to seconds
                return False

            # Wait for a short interval before checking again
            time.sleep(0.2)

    def new_delivery_mission(self, json):
        try:
            # check available delivery mission
            id = self.nwdb.get_available_delivery_id()
            if id == None:
                print('There is no any available delivery misssion!!')
                return False

            # configure the delivery mission
            # a_delivery_mission: NWSchema
            a_delivery_mission = self.nwdb.configure_delivery_mission(available_delivery_id=id)
            print(a_delivery_mission.receiver_id)
            print(f'[new_delivery_mission]: Get a delivery mission!!!')

            #region Notify the receiver
            #endregion

            #region ROBOT CONFIGURATION
            self.rmapi.write_robot_skill_to_properties(self.robot_rm_guid)
            print(f'[new_delivery_mission]: write Robot Skill...')
            skill_config = umethods.load_config('./models/conf/rm_skill.properties')
            #endregion
            print(f'[new_delivery_mission]: Loaded Robot Skill...')

            # get sender info
            # get origin location
            # get receiver info
            # get destination location

            # pos_origin details
            # pos_origin: RMSchema
            pos_destination = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_destination_id)
            print(f'[new_delivery_mission]: get_delivery_position_detail...')

            # get destination_id and then create a rm_guid first.

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(pos_destination.layout_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(pos_destination.layout_guid, pos_destination.x, pos_destination.y,
                                              pos_destination.heading)
            print(f'layout_id: {pos_destination.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_destination.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(skill_config.get('RM-Skill', 'RM-GOTO'),
                                        pos_destination.layout_guid,
                                        latest_marker_id,
                                        order=1,
                                        map_id=pos_destination.map_guid,
                                        pos_name=pos_destination.pos_name,
                                        x=pos_destination.x,
                                        y=pos_destination.y,
                                        heading=pos_destination.y)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[new_delivery_mission]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos_destination.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    # Charging
    def charging_mission_publisher(self, task_json, status_callback):

        done = self.charging_goto(task_json)
        if not done: return False
        done = self.wait_for_job_done(duration_min=5)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        done = self.charging_on(task_json, status_callback)
        if not done: return False

        return True

    def charging_goto(self):
        try:
            #region Notify the receiver
            #endregion

            # # charging_station_detail
            charging_station_id = self.nwdb.get_available_charging_station_id(self.robot_nw_id)
            charging_station = self.nwdb.get_charing_station_detail(charging_station_id) 

            # pos_origin details
            # pos_origin: NWSchema
            # pos_origin = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_origin_id)
            # pos_origin = NWSchema.DeliveryPose
            map_x, map_y, map_heading = self.T_RM.find_cur_map_point(charging_station.pos_x, charging_station.pos_y, charging_station.pos_theta)
            print(f'[charging_goto]: goto...')

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(charging_station.layout_rm_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(charging_station.layout_rm_guid, map_x, map_y, map_heading)
            print(f'layout_rm_guid: {charging_station.layout_rm_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(charging_station.layout_rm_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'RM-GOTO'),
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

            self.rmapi.new_job(self.robot_rm_guid, charging_station.layout_rm_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    def charging_on(self):
        """
        Interact with RM API
        """
        try:
            # # charging_station_detail
            charging_station_id = self.nwdb.get_available_charging_station_id(self.robot_nw_id)
            charging_station_detail = self.nwdb.get_charing_station_detail(charging_station_id)
            # Job-Delivery START
            # TASK START
            tasks = []
            print(f'layout_id: {charging_station_detail.layout_rm_guid}')
            # latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_destination.layout_guid)
            # print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            task = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-ON'),
                                       charging_station_detail.layout_rm_guid)
            tasks.append(task)
            print(task)
            # TASK END
            print(f'[charging_on]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid,
                               charging_station_detail.layout_rm_guid,
                               tasks=tasks,
                               job_name='DELIVERY-WAITUNLOADING')
            print(f'[charging_on]: configure job end...')

            return True
        except:
            return False

    def charging_off(self):
        """
        Interact with RM API
        """
        try:
            # # charging_station_detail
            charging_station_id = self.nwdb.get_available_charging_station_id(self.robot_nw_id)
            charging_station_detail = self.nwdb.get_charing_station_detail(charging_station_id)
            # Job-Delivery START
            # TASK START
            tasks = []
            print(f'layout_id: {charging_station_detail.layout_rm_guid}')
            # latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_destination.layout_guid)
            # print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            task = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-OFF'),
                                       charging_station_detail.layout_rm_guid)
            tasks.append(task)
            print(task)
            # TASK END
            print(f'[charging_on]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid,
                               charging_station_detail.layout_rm_guid,
                               tasks=tasks,
                               job_name='DELIVERY-WAITUNLOADING')
            print(f'[charging_on]: configure job end...')

            return True
        except:
            return False

    def rv_charging_start(self, task_json, status_callback):
        """
        Interact with RV API
        """
        try:
            # step 0. init. clear current task
            self.cancel_moving_task()

            time.sleep(1)
            self.rvapi.post_charging(upperLimit=100, duration_min=60, shutdownAfterCharging=False)

            thread = threading.Thread(target=self.thread_check_charging_status, args=(task_json, status_callback))
            thread.setDaemon(True)
            thread.start()

            return True
        except:
            return False

    def rv_charging_stop(self, task_json, status_callback):
        try:
            # stop charging
            self.rvapi.delete_charging()

            # get charging status. if NOT_CHARGING
            while (self.rvapi.get_charging_feedback() != 'NOT_CHARGING'):
                time.sleep(1)

            # goto charging position.
            self.goto(task_json, status_callback)

            return True
        except:
            
            return False      
         
    ## Methods
    ### Lift
    def robocore_call_lift(self, target_floor_int):  
        try:
            # # print(f'robocore_call_lift: {task_json}')
            # # mapId = task_json['parameters']['mapId']
            # mapId = self.get_current_map_rm_guid()
            
            # # need to get target_floor_int
            # # mapId -> nw_layout_id -> nw_floor_id
            # target_layout_id = self.nwdb.get_single_value('robot.map', 'layout_id', 'rm_guid', f'"{mapId}"')
            # target_floor_int = self.nwdb.get_single_value('robot.map.layout', 'floor_id', 'ID', target_layout_id)

            while(self.emsdlift.occupied):
                print(f'[robocore_call_lift] try to call emsd lift... wait for available...')
                time.sleep(2)
            
            # keep calling the lift
            while(True):
                # check if available
                if(self.emsdlift.occupied):
                    print(f'[robocore_call_lift] try to call emsd lift... wait for available...')
                    time.sleep(2)
                    continue
                
                # check if at current floor
                if(self.emsdlift.is_arrived(target_floor_int)):
                    print(f'[robocore_call_lift] try to call emsd lift... already at current floor...')
                    break

                # try to call lift
                # print(f'press rm_button: {target_floor_int}')
                is_pressed  = self.emsdlift.rm_to(target_floor_int)
                print(f'target_floor_int {target_floor_int}')
                if(not is_pressed):
                    print(f'[robocore_call_lift] try to call emsd lift... press button failed, retry...')    
                    continue
                
                print(f'[robocore_call_lift] called emsd lift... wait for arriving...')
                break

            # keep checking if lift is arrived
            while(True):
                if(self.emsdlift.is_arrived(target_floor_int)):
                    print(f'[robocore_call_lift] arrived!')

                    # hold the lift
                    print(f'[robocore_call_lift] hold the lift door for 5 minutes!')
                    self.emsdlift.open(10 * 60 * 5) # 10 = 1s

                    break
                else:
                    print(f'[robocore_call_lift] wait for arriving...')
                    time.sleep(2)

            return True
        except:
            return False

    def robocore_call_lift2(self, target_floor_int):  
            try:
                # keep calling the lift
                # keep checking if lift is arrived
                while(True):
                    if(self.emsdlift.occupied):
                        # print(f'[robocore_call_lift] try to call emsd lift... wait for available...')
                        print(f'[robocore_call_lift] emsd lift occupied... wait for available...')
                        time.sleep(1)
                        continue
                    elif(self.emsdlift.is_arrived(target_floor_int) and not self.emsdlift.is_anykey_pressed()):
                        is_open_and_hold = self.emsdlift.open(10 * 60 * 5) # 10 = 1s
                        if(is_open_and_hold):
                            print(f'[robocore_call_lift] arrived!')
                            print(f'[robocore_call_lift] hold the lift door for 5 minutes!')
                            break
                        else:
                            self.emsdlift.release_all_keys()
                    else:
                        is_pressed = self.emsdlift.rm_to(target_floor_int)
                        print(f'target_floor_int; {target_floor_int}')
                        if(is_pressed):
                            print(f'[robocore_call_lift] pressed button successful, wait for arriving...')
                        else:
                            print(f'[robocore_call_lift] press button failed, retry...')                   
                        time.sleep(2)
                        continue

                return True
            except:
                return False

    ## Mission Designer
    ### Delivery
    def delivery_mission_publisher(self):

        a_delivery_mission = self.get_delivery_mission_detail()

        # to sender
        done = self.pub_delivery_goto_sender(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_ToSender.value, self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=25)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # loading package
        done = self.pub_delivery_wait_for_loading(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_WaitForLoading.value, self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=15)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # to receiver
        done = self.pub_delivery_goto_receiver(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_ToReceiver.value, self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=25)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # unloading package
        done = self.pub_delivery_wait_for_unloading(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_WaitForUnloading.value,
                                         self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=15)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # back to charging stataion:  
        # 1. goto
        done = self.charging_goto()
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_BackToChargingStation.value, self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=15)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # 2. charging
        done = self.charging_on()
        if not done: return False
        done = self.wait_for_job_done(duration_min=15)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # finish. status -> Idle and wait for next mission...
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Null.value, self.a_delivery_mission.ID)
        self.nwdb.update_single_value('ui.display.status','ui_flag',0,'robot_id',self.robot_nw_id)
        self.delivery_clear_positions(self.a_delivery_mission)
        return True

    ### Lift
    def lift_mission_publisher(self):

        target_map_rm_guid = self.last_goto_json['parameters']['mapId']
        target_layout_id = self.nwdb.get_single_value('robot.map', 'layout_id', 'rm_guid', f'"{target_map_rm_guid}"')
        print(f'[lift-debug] target_map_rm_guid: {target_map_rm_guid}')
        print(f'[lift-debug] target_layout_id: {target_layout_id}')
                
        a_lift_mission = self.get_lift_mission_detail(self.layout_nw_id, target_layout_id)

        # to CurWaitingPos
        done = self.pub_goto_liftpos(a_lift_mission, NWEnum.LiftPositionType.CurWaitingPos)
        if not done: return False
        print(f'[lift_mission] Flag1: to CurWaitingPos...')
        done = self.wait_for_job_done(duration_min=10)  # wait for job is done
        if not done: return False  # stop assigning lift mission

        # localization to liftmap
        done = self.pub_localize_liftmap_pos(a_lift_mission, NWEnum.LiftPositionType.LiftMapIn)
        if not done: return False
        print(f'[lift_mission] Flag2: Localize LiftMapIn...')
        done = self.wait_for_job_done(duration_min=10)  # wait for job is done
        if not done: return False  # stop assigning lift mission

        # to LiftMapTransitPos, Pause Robot, Call Lift, Unpasue Robot
        done = self.pub_goto_liftpos(a_lift_mission, NWEnum.LiftPositionType.LiftMapTransit)
        if not done: return False
        print(f'[lift_mission] Flag3:  to LiftMapTransitPos...')
        self.rvjoystick.enable()
        self.robocore_call_lift2(a_lift_mission.cur_floor_int)
        time.sleep(1)
        self.rvjoystick.disable()
        done = self.wait_for_job_done(duration_min=10)  # wait for job is done
        if not done: return False  # stop assigning lift mission
        
        # to press target floor button and release the door
        self.func_lift_pressbutton_releasedoor(a_lift_mission)
        # threading.Thread(target=self.func_lift_pressbutton_releasedoor, args=(a_lift_mission)).start()

        # to LiftMapOut
        done = self.pub_goto_liftpos(a_lift_mission, NWEnum.LiftPositionType.LiftMapOut)
        if not done: return False
        print(f'[lift_mission] Flag7: to LiftMapOut...')
        # **check if lift is arrived, hold the lift door
        # self.thread_check_lift_arrive(a_lift_mission)
        self.thread_check_lift_arrive2(a_lift_mission.target_floor_int)
        # threading.Thread(target=self.thread_check_lift_arrive, args=(a_lift_mission,)).start()
        done = self.wait_for_job_done(duration_min=15)  # wait for job is done
        if not done: return False  # stop assigning lift mission

        # **release the lift door
        self.emsdlift.release_all_keys()
        self.emsdlift.close()
        print(f'[lift_mission] Flag8:  close lift door...')

        # localization to liftmap
        done = self.pub_localize_liftpos(a_lift_mission, NWEnum.LiftPositionType.TargetOutPos)
        if not done: return False
        print(f'[lift_mission] Flag2: Localize TargetOutPos...')
        done = self.wait_for_job_done(duration_min=10)  # wait for job is done
        if not done: return False  # stop assigning lift mission

        # to Last GOTO Position
        done = self.pub_last_goto()
        if not done: return False
        print(f'[lift_mission] Flag9: to LastGotoPos...')
        done = self.wait_for_job_done(duration_min=10)  # wait for job is done
        if not done: return False  # stop assigning lift mission

        return True
    
    def thread_check_lift_arrive(self, target_floor_int):
        # pasue robot first!
        self.rvjoystick.enable()

        while(True):
            if(self.emsdlift.is_arrived(target_floor_int)):
                print(f'[lift_mission] Flag6:  lift is arrived,...')
                # hold the lift
                print(f'[robocore_call_lift] Flag6: hold the lift door for 5 minutes!')
                self.emsdlift.open(10 * 60 * 5) # 10 = 1s
                # release robot manual mode!
                time.sleep(2)
                self.rvjoystick.disable()

                break
            print(f'[lift_mission] Flag6:  wait for lift arriving at target_floor_int {target_floor_int}...')
            time.sleep(0.5)
        print(f'[thread_check_lift_arrive] finished')

    def thread_check_lift_arrive2(self, target_floor_int):
        try:
            # pasue robot first!
            self.rvjoystick.enable()            

            # keep calling the lift
            while(True):
                
                if(self.emsdlift.occupied):
                    # print(f'[robocore_call_lift] try to call emsd lift... wait for available...')
                    print(f'[robocore_call_lift] emsd lift occupied... wait for available...')
                    time.sleep(2)
                    continue
                elif(self.emsdlift.is_arrived(target_floor_int) and not self.emsdlift.is_anykey_pressed()):
                    is_open_and_hold = self.emsdlift.open(10 * 60 * 5) # 10 = 1s
                    if(is_open_and_hold):
                        print(f'[robocore_call_lift] arrived!')
                        print(f'[robocore_call_lift] hold the lift door for 5 minutes!')
                        # release robot manual mode!
                        time.sleep(1)
                        self.rvjoystick.disable()
                        break
                    else:
                        self.emsdlift.release_all_keys()                  
                else:
                    is_pressed = self.emsdlift.rm_to(target_floor_int)
                    if(is_pressed):
                        print(f'[robocore_call_lift] pressed button successful, wait for arriving...')
                    else:
                        print(f'[robocore_call_lift] press button failed, retry...')                   
                    time.sleep(2)
                    continue
            return True
        except:
            return False

    def func_lift_pressbutton_releasedoor(self, a_lift_mission):
        print(f'[func_lift_pressbutton_releasedoor] start...')
        while(True):
            print(f'press rm_button: {a_lift_mission.target_floor_int}')
            is_pressed  = self.emsdlift.rm_to(a_lift_mission.target_floor_int)
            if(not is_pressed):
                print(f'[robocore_call_lift] try to call emsd lift... press button failed, retry...')    
                
                # **release the lift door
                self.emsdlift.release_all_keys()
                self.emsdlift.close()
                print(f'[lift_mission] Flag4:  close lift door...')
                continue

            # **release the lift door
            self.emsdlift.release_all_keys()
            self.emsdlift.close()
            print(f'[lift_mission] Flag4:  close lift door...')
                
            print(f'[robocore_call_lift] called emsd lift... wait for arriving...')
            break

    def func_lift_checkarrive_holddoor(self,a_lift_mission):
        print(f'[func_lift_checkarrive_holddoor] start...')
        while(True):
            if(self.emsdlift.is_arrived(a_lift_mission.target_floor_int)):
                print(f'[lift_mission] Flag6:  lift is arrived,...')
                # hold the lift
                print(f'[robocore_call_lift] Flag6: hold the lift door for 5 minutes!')
                self.emsdlift.open(10 * 60 * 5) # 10 = 1s
                break

            print(f'[lift_mission] Flag6:  wait for lift arriving at target_floor_int {a_lift_mission.target_floor_int}...')
            time.sleep(2)
        
    ## Publish RM Mission
    ### Delivery
    def pub_delivery_goto_charging_station(self, charging_station: NWSchema.ChargingStation):
        try:
            #region Notify the receiver
            #endregion

            # pos_origin details
            # pos_origin: RMSchema
            pos_origin = self.nwdb.get_delivery_position_detail(charging_station.pos_origin_id)
            map_x, map_y, map_heading = self.T_RM.find_cur_map_point(charging_station.pos_x, charging_station.pos_y, charging_station.pos_theta)
            pos_origin.x = map_x
            pos_origin.y = map_y
            pos_origin.heading = map_heading
            print(f'[new_delivery_mission]: get_delivery_position_detail...')

            # get destination_id and then create a rm_guid first.

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(pos_origin.layout_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(pos_origin.layout_guid, pos_origin.x, pos_origin.y, pos_origin.heading)
            print(f'layout_id: {pos_origin.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_origin.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'RM-GOTO'),
                                        pos_origin.layout_guid,
                                        latest_marker_id,
                                        order=1,
                                        map_id=pos_origin.map_guid,
                                        pos_name=pos_origin.pos_name,
                                        x=pos_origin.x,
                                        y=pos_origin.y,
                                        heading=pos_origin.heading)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[new_delivery_mission]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-Charging-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False
    
    def pub_delivery_goto_sender(self, a_delivery_mission: NWSchema.DeliveryMission):
        try:
            #region Notify the receiver
            #endregion

            # pos_origin details
            # pos_origin: RMSchema
            pos_origin = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_origin_id)
            map_x, map_y, map_heading = self.T_RM.find_cur_map_point(pos_origin.x, pos_origin.y, pos_origin.heading)
            pos_origin.x = map_x
            pos_origin.y = map_y
            pos_origin.heading = map_heading
            print(f'[new_delivery_mission]: get_delivery_position_detail...')

            # get destination_id and then create a rm_guid first.

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(pos_origin.layout_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(pos_origin.layout_guid, pos_origin.x, pos_origin.y, pos_origin.heading)
            print(f'layout_id: {pos_origin.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_origin.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'RM-GOTO'),
                                        pos_origin.layout_guid,
                                        latest_marker_id,
                                        order=1,
                                        map_id=pos_origin.map_guid,
                                        pos_name=pos_origin.pos_name,
                                        x=pos_origin.x,
                                        y=pos_origin.y,
                                        heading=pos_origin.heading)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[new_delivery_mission]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    def pub_delivery_goto_receiver(self, a_delivery_mission: NWSchema.DeliveryMission):
        try:
            #region Notify the receiver
            #endregion

            # pos_origin details
            # pos_origin: RMSchema
            pos_destination = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_destination_id)
            pos_destination.x, pos_destination.y, pos_destination.heading = self.T_RM.find_cur_map_point(pos_destination.x, pos_destination.y, pos_destination.heading)
            print(f'[new_delivery_mission]: get_delivery_position_detail...')

            # get destination_id and then create a rm_guid first.

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(pos_destination.layout_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(pos_destination.layout_guid, pos_destination.x, pos_destination.y,
                                              pos_destination.heading)
            print(f'layout_id: {pos_destination.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_destination.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'RM-GOTO'),
                                        pos_destination.layout_guid,
                                        latest_marker_id,
                                        order=1,
                                        map_id=pos_destination.map_guid,
                                        pos_name=pos_destination.pos_name,
                                        x=pos_destination.x,
                                        y=pos_destination.y,
                                        heading=pos_destination.heading)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[new_delivery_mission]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos_destination.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    def pub_delivery_wait_for_loading(self, a_delivery_mission: NWSchema.DeliveryMission):
        try:
            # pos_origin details
            pos_origin = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_origin_id)
            print(f'[delivery_wait_for_loading]: get_pos_origin_detail...')

            # Job-Delivery START
            # TASK START
            tasks = []
            print(f'layout_id: {pos_origin.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_origin.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            task = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'DELIVERY-LOADING-PACKAGE'),
                                       pos_origin.layout_guid)
            tasks.append(task)
            print(task)
            # TASK END
            print(f'[delivery_wait_for_loading]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-WAITLOADING')
            print(f'[delivery_wait_for_loading]: configure job end...')

            return True
        except:
            return False

    def pub_delivery_wait_for_unloading(self, a_delivery_mission: NWSchema.DeliveryMission):
        try:
            # pos_origin details
            pos_destination = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_destination_id)
            print(f'[delivery_wait_for_unloading]: get_pos_origin_detail...')

            # Job-Delivery START
            # TASK START
            tasks = []
            print(f'layout_id: {pos_destination.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_destination.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            task = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'DELIVERY-UNLOADING-PACKAGE'),
                                       pos_destination.layout_guid)
            tasks.append(task)
            print(task)
            # TASK END
            print(f'[delivery_wait_for_unloading]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid,
                               pos_destination.layout_guid,
                               tasks=tasks,
                               job_name='DELIVERY-WAITUNLOADING')
            print(f'[delivery_wait_for_unloading]: configure job end...')

            return True
        except:
            return False

    ### Lift
    def pub_goto_liftpos(self, a_lift_mission: NWSchema.LiftMission, pos_type: NWEnum.LiftPositionType):
        try:
            # pos_origin details
            # pos_origin: RMSchema
            if  (pos_type == NWEnum.LiftPositionType.CurWaitingPos): 
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.cur_waiting_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.CurTransitPos):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.cur_transit_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.TargetWaitingPos): 
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_waiting_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.TargetTransitPos):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_transit_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.TargetOutPos):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_out_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.LiftMapIn):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.liftmap_in_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.LiftMapTransit):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.liftmap_transit_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.LiftMapOut):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.liftmap_out_pos_id)
            
            map_x, map_y, map_heading = self.T_RM.find_cur_map_point(pos_origin.x, pos_origin.y, pos_origin.heading)
            pos_origin.x = map_x
            pos_origin.y = map_y
            pos_origin.heading = map_heading
            print(f'[new_delivery_mission]: get_lift_position_detail...')

            # get destination_id and then create a rm_guid first.

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(pos_origin.layout_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(pos_origin.layout_guid, pos_origin.x, pos_origin.y, pos_origin.heading)
            print(f'layout_id: {pos_origin.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_origin.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'RM-GOTO'),
                                        pos_origin.layout_guid,
                                        latest_marker_id,
                                        order=1,
                                        map_id=pos_origin.map_guid,
                                        pos_name=pos_origin.pos_name,
                                        x=pos_origin.x,
                                        y=pos_origin.y,
                                        heading=pos_origin.heading)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[new_delivery_mission]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    def pub_localize_liftmap_pos(self, a_lift_mission: NWSchema.LiftMission, pos_type: NWEnum.LiftPositionType):
            try:
                # pos_origin details
                # pos_origin: RMSchema
                if  (pos_type == NWEnum.LiftPositionType.CurWaitingPos): 
                    pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.cur_waiting_pos_id)
                elif(pos_type == NWEnum.LiftPositionType.CurTransitPos):
                    pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.cur_transit_pos_id)
                elif(pos_type == NWEnum.LiftPositionType.TargetWaitingPos): 
                    pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_waiting_pos_id)
                elif(pos_type == NWEnum.LiftPositionType.TargetTransitPos):
                    pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_transit_pos_id)
                elif(pos_type == NWEnum.LiftPositionType.LiftMapIn):
                    pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.liftmap_in_pos_id)
                elif(pos_type == NWEnum.LiftPositionType.LiftMapTransit):
                    pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.liftmap_transit_pos_id)
                elif(pos_type == NWEnum.LiftPositionType.LiftMapOut):
                    pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.liftmap_out_pos_id)
                
                target_layout_rm_guid = self.nwdb.get_single_value('robot.map.layout', 'rm_guid', 'ID', a_lift_mission.liftmap_layout_id)
                target_map_rm_guid = self.nwdb.get_single_value('robot.map', 'rm_guid', 'layout_id', a_lift_mission.liftmap_layout_id)
                params = self.rmapi.get_layout_map_list(target_layout_rm_guid, target_map_rm_guid)
                # print('<debug> liftmap_pos')
                self.T_RM.update_layoutmap_params(params.imageWidth, params.imageHeight, 
                                                params.scale, params.angle, params.translate)
                map_x, map_y, map_heading = self.T_RM.find_cur_map_point(pos_origin.x, pos_origin.y, pos_origin.heading)
                pos_origin.x = map_x
                pos_origin.y = map_y
                pos_origin.heading = map_heading
                # print(f'[xxx] heading: {map_heading}')
                print(f'[pub_localize_liftmap_pos]: get_lift_position_detail...')

                # get destination_id and then create a rm_guid first.

                # Job-Delivery START
                # TASK START
                tasks = []
                self.rmapi.delete_all_delivery_markers(pos_origin.layout_guid)
                # configure task-01: create a new position on RM-Layout
                self.rmapi.create_delivery_marker(pos_origin.layout_guid, pos_origin.x, pos_origin.y, pos_origin.heading)
                print(f'layout_id: {pos_origin.layout_guid}')
                latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_origin.layout_guid)
                print(f'latest_marker_id: {latest_marker_id}')
                # configure task-01: create a new task
                goto = self.rmapi.task_localize(self.skill_config.get('RM-Skill', 'RM-LOCALIZE'),
                                            pos_origin.layout_guid,
                                            latest_marker_id,
                                            order=1,
                                            map_id=pos_origin.map_guid,
                                            pos_name=pos_origin.pos_name,
                                            x=pos_origin.x,
                                            y=pos_origin.y,
                                            heading=pos_origin.heading)
                tasks.append(goto)
                print(goto)
                # TASK END
                print(f'[pub_localize_liftpos]: configure task end...')

                self.rmapi.new_job(self.robot_rm_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
                print(f'[pub_localize_liftpos]: configure job end...')

                return True
            except:
                return False

    def pub_localize_liftpos(self, a_lift_mission: NWSchema.LiftMission, pos_type: NWEnum.LiftPositionType):
        try:
            # pos_origin details
            # pos_origin: RMSchema
            if  (pos_type == NWEnum.LiftPositionType.CurWaitingPos): 
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.cur_waiting_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.CurTransitPos):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.cur_transit_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.TargetWaitingPos): 
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_waiting_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.TargetTransitPos):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_transit_pos_id)
            elif(pos_type == NWEnum.LiftPositionType.TargetOutPos):
                pos_origin = self.nwdb.get_lift_position_detail(a_lift_mission.target_out_pos_id)
            
            target_layout_rm_guid = self.nwdb.get_single_value('robot.map.layout', 'rm_guid', 'ID', a_lift_mission.target_layout_id)
            target_map_rm_guid = self.nwdb.get_single_value('robot.map', 'rm_guid', 'layout_id', a_lift_mission.target_layout_id)
            params = self.rmapi.get_layout_map_list(target_layout_rm_guid, target_map_rm_guid)
            # print('<debug>layout_pose 2')
            self.T_RM.update_layoutmap_params(params.imageWidth, params.imageHeight, 
                                              params.scale, params.angle, params.translate)
            map_x, map_y, map_heading = self.T_RM.find_cur_map_point(pos_origin.x, pos_origin.y, pos_origin.heading)
            pos_origin.x = map_x
            pos_origin.y = map_y
            pos_origin.heading = map_heading
            # print(f'[xxx] heading: {map_heading}')
            print(f'[pub_localize_liftpos]: get_lift_position_detail...')

            # get destination_id and then create a rm_guid first.

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(pos_origin.layout_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(pos_origin.layout_guid, pos_origin.x, pos_origin.y, pos_origin.heading)
            print(f'layout_id: {pos_origin.layout_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(pos_origin.layout_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_localize(self.skill_config.get('RM-Skill', 'RM-LOCALIZE'),
                                        pos_origin.layout_guid,
                                        latest_marker_id,
                                        order=1,
                                        map_id=pos_origin.map_guid,
                                        pos_name=pos_origin.pos_name,
                                        x=pos_origin.x,
                                        y=pos_origin.y,
                                        heading=pos_origin.heading)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[pub_localize_liftpos]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[pub_localize_liftpos]: configure job end...')

            return True
        except:
            return False

    def pub_call_lift(self, a_lift_mission: NWSchema.LiftMission):
        try:
            print(f'[pub_call_lift]: ...')
            # a_lift_mission.cur_floor_int
            pos = self.nwdb.get_lift_position_detail(a_lift_mission.cur_waiting_pos_id)

            # Job-Delivery START
            # TASK START
            tasks = []
            # print(f'layout_id: {pos.layout_guid}')
            # configure task-01: create a new task
            task = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'ROBOCORE-CALL-LIFT'),
                                       pos.layout_guid)
            tasks.append(task)
            print(task)
            # TASK END
            print(f'[pub_call_lift]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, pos.layout_guid, tasks=tasks, job_name='DELIVERY-WAITLOADING')
            print(f'[pub_call_lift]: configure job end...')

            return True
        except:
            return False
        pass
    
    def pub_last_goto(self):
        try:
            task_json = self.last_goto_json
            # pos_origin details
            map_rm_guid = task_json['parameters']['mapId']
            pos_name = task_json['parameters']['positionName']
            pos_x = task_json['parameters']['x']
            pos_y = task_json['parameters']['y']
            pos_theta = task_json['parameters']['heading']
            layout_nw_id = self.nwdb.get_single_value('robot.map', 'layout_id', 'rm_guid', map_rm_guid)
            layout_rm_guid = self.nwdb.get_single_value('robot.map.layout', 'rm_guid', 'ID', layout_nw_id)
            # pos_origin: RMSchema
            print(f'[lift]: pub_last_goto...')

            # get destination_id and then create a rm_guid first.

            # Job-Delivery START
            # TASK START
            tasks = []
            self.rmapi.delete_all_delivery_markers(layout_rm_guid)
            # configure task-01: create a new position on RM-Layout
            self.rmapi.create_delivery_marker(layout_rm_guid, pos_x, pos_y, pos_theta)
            print(f'layout_id: {layout_rm_guid}')
            latest_marker_id = self.rmapi.get_latest_delivery_marker_guid(layout_rm_guid)
            print(f'latest_marker_id: {latest_marker_id}')
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'RM-GOTO'),
                                        layout_rm_guid,
                                        latest_marker_id,
                                        order=1,
                                        map_id=map_rm_guid,
                                        pos_name=pos_name,
                                        x=pos_x,
                                        y=pos_y,
                                        heading=pos_theta)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[new_delivery_mission]: configure task end...')

            self.rmapi.new_job(self.robot_rm_guid, layout_rm_guid, tasks=tasks, job_name='Lift-LAST-GOTO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False
        
if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    skill_config_path = './conf/rm_skill.properties'

    robot = Robot(config, port_config, skill_config_path)

    # a_lift_mission = robot.get_lift_mission_detail(5, 6)

    # robot.pub_call_lift(a_lift_mission)

    robot.robocore_call_lift2(4)
    # robot.charging_on()
    # robot.charging_off()
    # robot.charging_goto()

    # robot.get_current_layout_pose()

    # # get status
    # robot.status_start(NWEnum.Protocol.RVAPI)
    # while(True):
    #     time.sleep(1)
    #     print(robot.status_summary())
    #     # print(robot.get_current_pose(NWEnum.Protocol.RVAPI))
    #     # print(robot.get_battery_state(NWEnum.Protocol.RVAPI))

    # robot.new_delivery_mission()
    
    # # followme testing
    # robot.follow_me_mode()
    # robot.is_paired()
    # robot.follow_me_pair()
    # robot.follow_me_unpair()

    # layout_id = robot.get_current_layout_id()

    # print(f'current layout_id: {layout_id}')
    
