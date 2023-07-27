import time
import threading
import logging
import src.utils.methods as umethods
import src.models.api_rv as RVAPI
import src.models.mqtt_rv as RVMQTT
import src.models.mqtt_rv2 as RVMQTT2
from src.models.mqtt_rv_joystick import RVJoyStick
import src.models.api_rm as RMAPI
import src.models.mqtt_nw as NWMQTT
import src.models.db_robot as RobotDB
import src.top_module.db_top_module as TopModuleDB
import src.models.trans_rvrm as Trans
# Schema
import src.models.schema.rm as RMSchema
import src.models.schema.nw as NWSchema
import src.models.schema.rv as RVSchema
# Enum
import src.models.enums.rm as RMEnum
import src.models.enums.nw as NWEnum
# top module
import src.top_module.enums.enums_module_status as MoEnum
from src.top_module.module import lift_levelling_module as MoLiftLevelling
from src.top_module.module import iaq as MoIAQ
from src.top_module.module import locker as MoLocker
from src.top_module.module.access_control_module import AccessControl as MoAccessControl
from src.top_module.sensor.gyro import Gyro as MoGyro


class Robot:
    def __init__(self, config, port_config, skill_config_path):
        self.rvapi = RVAPI.RVAPI(config)
        self.rvmqtt = RVMQTT.RVMQTT(config)
        self.rvjoystick = RVJoyStick(config)
        self.rmapi = RMAPI.RMAPI(config)
        self.nwmqtt = NWMQTT.NWMQTT(config, port_config)
        self.nwdb = RobotDB.robotDBHandler(config)
        self.modb = TopModuleDB.TopModuleDBHandler(config, self.status_summary)
        self.T = Trans.RVRMTransform()
        self.config = config
        self.port_config = port_config
        # self.rvmqtt.start() # for RVMQTT.RVMQTT
        self.nwmqtt.start()

        # # # module - models/sensors
        self.mo_lift_levelling = MoLiftLevelling.LiftLevellingModule(self.modb, config, port_config, self.status_summary)
        self.mo_iaq = MoIAQ.IaqSensor(self.modb, config, port_config, self.status_summary, Ti=2)
        self.mo_locker = MoLocker.Locker(port_config)
        self.mo_access_control = MoAccessControl(self.modb, config, port_config)
        self.mo_gyro = MoGyro(self.modb, config, port_config, self.status_summary)

        # self.module_lift_inspect =Modules.LiftInspectionSensor()
        # self.module_internal = Modules.InternalDevice()
        # self.module_monitor = Modules.Monitor()
        # self.modmodule_phone = Modules.PhoneDevice()

        ## robot baisc info
        self.ipc_ip_addr = config.get('IPC', 'localhost')
        self.surface_ip_addr = config.get('SURFACE', 'localhost')
        self.robot_id = self.nwdb.robot_id
        self.robot_guid = self.nwdb.robot_guid
        self.robot_status = RMSchema.Status(0.0, 0, RMSchema.mapPose())
        self.map_id = None
        self.a_delivery_mission = None
        self.robot_locker_is_closed = self.locker_is_closed()

        ## delivery related
        #region ROBOT CONFIGURATION
        self.rmapi.write_robot_skill_to_properties(self.robot_guid, skill_config_path)
        # print(f'[new_delivery_mission]: write Robot Skill...')
        self.skill_config = umethods.load_config(skill_config_path)
        # print(f'[new_delivery_mission]: Loaded Robot Skill...')
        #endregion

        ## nw-door-agent
        self.door_agent_start = False
        self.door_agent_finish = False

    def sensor_start(self):
        self.mo_iaq.start()
        # self.mo_access_control.start()
        print(f'[robot.sensor_start]: Start...')

    def status_start(self, protocol: NWEnum.Protocol):
        threading.Thread(target=self.update_status, args=(protocol, )).start()  # from RV API
        print(f'[robot.status_start]: Start...')

    def update_status(self, protocol):  # update thread
        while True:
            try:
                # # rm status <--- rv status
                self.robot_status.state = 1  # todo: robot status
                self.robot_status.mapPose.mapId = self.get_current_map_rm_guid()  # map
                self.robot_status.batteryPct = self.get_battery_state(protocol)  # battery
                pixel_x, pixel_y, heading = self.get_current_pose(protocol)  # current pose
                # print(pixel_x, pixel_y, heading)
                self.robot_status.mapPose.x = pixel_x
                self.robot_status.mapPose.y = pixel_y
                self.robot_status.mapPose.heading = heading

                # Modules
                self.robot_locker_is_closed = self.locker_is_closed()

                ## TO NWDB
                self.map_id = self.get_current_map_id()
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
        battery = self.robot_status.batteryPct
        x = self.robot_status.mapPose.x
        y = self.robot_status.mapPose.y
        theta = self.robot_status.mapPose.heading
        map_id = self.map_id
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
        map_id = self.map_id
        x = self.robot_status.mapPose.x
        y = self.robot_status.mapPose.y
        theta = self.robot_status.mapPose.heading
        
        return RMSchema.mapPose(map_id, x, y, theta)

    def get_current_map_id(self):
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

    def get_current_layout_id(self):
        try:
            map_id = self.get_current_map_id()
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
            # step 0. init. clear current task
            self.cancel_moving_task()
            # step 1. parse task json
            # print('step 1')
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            rv_map_name = self.nwdb.get_map_amr_guid(rm_map_metadata.mapId)
            rv_map_metadata = self.rvapi.get_map_metadata(rv_map_name)
            # step 2. transformation. rm2rv
            # print('step 2')
            self.T.update_rv_map_info(rv_map_metadata.width, rv_map_metadata.height, rv_map_metadata.x,
                                      rv_map_metadata.y, rv_map_metadata.angle)
            rv_waypoint = self.T.waypoint_rm2rv(rv_map_name, rm_map_metadata.positionName, rm_map_metadata.x,
                                                rm_map_metadata.y, rm_map_metadata.heading)
            # step 3. rv. create point base on rm. localization.
            # print('step 3')
            self.rvapi.delete_all_waypoints(rv_map_name)
            self.rvapi.post_new_waypoint(rv_waypoint.mapName, rv_waypoint.name, rv_waypoint.x, rv_waypoint.y,
                                         rv_waypoint.angle)
            self.rvapi.change_mode_navigation()
            self.rvapi.change_map(rv_map_name)
            self.rvapi.update_initial_pose(rv_waypoint.x, rv_waypoint.y, rv_waypoint.angle)
            # step 4. double check
            # print('step 4')
            pose_is_valid = True
            # pose_is_valid = self.rvapi.check_current_pose_valid()
            map_is_active = self.rvapi.get_active_map().name == rv_map_name
            if (pose_is_valid & map_is_active): return True
            else: return False
        except:
            return False

    # status_callback: check task_handler3.py
    def goto(self, task_json, status_callback):
        try:
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
                                                rm_map_metadata.y, rm_map_metadata.heading)
            # step3. rv. create point base on rm. localization.
            # print('step3')
            self.rvapi.delete_all_waypoints(rv_map_name)
            pose_name = 'TEMP'
            time.sleep(1)
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
                status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Complete)

            if (status == 'PRE_CHARGING' or status == 'CHARGING' or status == 'POST_CHARGING'):
                print('[charging.check_mission_status] robot is charging...')
                time.sleep(1)
                continue

        print('[charging.check_mission_status] Exiting...')

    def thread_check_mission_status(self, task_json, status_callback):

        self.door_agent_start = True  # door-agent logic

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
                    status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Complete)

                # # if error
                # if(self.check_goto_has_error):
                #     print('flag error') # throw error log
                #     status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Fail)
                # if cancelled
                if (self.check_goto_is_cancelled()):
                    print('[goto.check_mission_status] robot has cancelled moving task')
                    status_callback(rm_task_data.taskId, rm_task_data.taskType, RMEnum.TaskStatusType.Fail)

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

            self.nwdb.insert_new_mission_id(self.robot_id, rm_mission_guid, NWEnum.MissionType.IAQ)
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

    # Module - IAQ - End

    # Module - Lift Inspection
    # todo: lift noise/ lift video/ lift height/ lift vibration/ lift levelling

    def lift_vibration_on(self, task_json):
        # try:
        self.mo_gyro = MoGyro(self.modb, self.config, self.port_config, self.status_summary)
        rm_mission_guid = self.rmapi.get_mission_id(task_json)
        self.nwdb.insert_new_mission_id(self.robot_id, rm_mission_guid, NWEnum.MissionType.LiftAcc)
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
            self.mo_lift_levelling = MoLiftLevelling.LiftLevellingModule(self.modb, self.config, self.port_config, self.status_summary)

            rm_mission_guid = self.rmapi.get_mission_id(task_json)
            self.nwdb.insert_new_mission_id(self.robot_id, rm_mission_guid, NWEnum.MissionType.LiftLevelling)
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

    def delivery_goto_sender(self, a_delivery_mission: NWSchema.DeliveryMission):
        try:
            #region Notify the receiver
            #endregion

            # pos_origin details
            # pos_origin: RMSchema
            pos_origin = self.nwdb.get_delivery_position_detail(a_delivery_mission.pos_origin_id)
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

            self.rmapi.new_job(self.robot_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    def delivery_goto_receiver(self, a_delivery_mission: NWSchema.DeliveryMission):
        try:
            #region Notify the receiver
            #endregion

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

            self.rmapi.new_job(self.robot_guid, pos_destination.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    def delivery_wait_for_loading(self, a_delivery_mission: NWSchema.DeliveryMission):
        try:
            #region Notify the receiver
            #endregion

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

            self.rmapi.new_job(self.robot_guid, pos_origin.layout_guid, tasks=tasks, job_name='DELIVERY-WAITLOADING')
            print(f'[delivery_wait_for_loading]: configure job end...')

            return True
        except:
            return False

    def delivery_wait_for_unloading(self, a_delivery_mission: NWSchema.DeliveryMission):
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

            self.rmapi.new_job(self.robot_guid,
                               pos_destination.layout_guid,
                               tasks=tasks,
                               job_name='DELIVERY-WAITUNLOADING')
            print(f'[delivery_wait_for_unloading]: configure job end...')

            return True
        except:
            return False

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
                time.sleep(1)
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
                time.sleep(1)
        except:
            return False

    # Delivery Publisher
    def delivery_mission_publisher(self):

        a_delivery_mission = self.get_delivery_mission_detail()

        # to sender
        done = self.delivery_goto_sender(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_ToSender.value, self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=5)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # loading package
        done = self.delivery_wait_for_loading(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_WaitForLoading.value, self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=15)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # to receiver
        done = self.delivery_goto_receiver(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_ToReceiver.value, self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=5)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # unloading package
        done = self.delivery_wait_for_unloading(a_delivery_mission)
        if not done: return False
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Active_WaitForUnloading.value,
                                         self.a_delivery_mission.ID)
        done = self.wait_for_job_done(duration_min=15)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        # back to charging stataion: 1. goto 2. charging
        time.sleep(2)
        self.nwdb.update_delivery_status(NWEnum.DeliveryStatus.Null.value, self.a_delivery_mission.ID)
        self.delivery_clear_positions(self.a_delivery_mission)
        return True

    ## Delivery Publisher Methods

    def wait_for_job_done(self, duration_min):
        print(f'[delivery]: wait for job done... duration: {duration_min} minutes')
        start_time = time.time()
        while True:
            # Check if the job is done (replace with your own condition)
            if self.rmapi.get_latest_mission_status() == RMEnum.MissionStatus.Completed:
                return True

            # Check if the specified duration has elapsed
            elapsed_time = time.time() - start_time
            if elapsed_time >= (duration_min * 60):  # Convert minutes to seconds
                return False

            # Wait for a short interval before checking again
            time.sleep(2)

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
            self.rmapi.write_robot_skill_to_properties(self.robot_guid)
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

            self.rmapi.new_job(self.robot_guid, pos_destination.layout_guid, tasks=tasks, job_name='DELIVERY-GOTO-DEMO')
            print(f'[new_delivery_mission]: configure job end...')

            return True
        except:
            return False

    # Charging

    def charging_mission_publisher(self, task_json, status_callback):

        done = self.assgin_job_CHARGING_GOTO(task_json)
        if not done: return False
        done = self.wait_for_job_done(duration_min=5)  # wait for job is done
        if not done: return False  # stop assigning delivery mission

        done = self.assign_job_CHARGING_START(task_json, status_callback)
        if not done: return False

        return True

    def assgin_job_CHARGING_GOTO(self, task_json):
        try:
            # Job START
            # TASK START
            tasks = []
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            layout_guid = self.rmapi.get_layout_guid(rm_map_metadata.mapId)
            layout_marker_guid = self.rmapi.get_layout_marker_guid(layout_guid, rm_map_metadata.positionName)
            # configure task-01: create a new task
            goto = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'RM-GOTO'),
                                        layout_guid,
                                        layout_marker_guid,
                                        order=1,
                                        map_id=rm_map_metadata.mapId,
                                        pos_name=rm_map_metadata.positionName,
                                        x=rm_map_metadata.x,
                                        y=rm_map_metadata.y,
                                        heading=rm_map_metadata.heading)
            tasks.append(goto)
            print(goto)
            # TASK END
            print(f'[new_goto_mission]: configure task end...')

            self.rmapi.new_job(self.robot_guid, layout_guid, tasks=tasks, job_name='CHARGING-GOTO-DEMO')
            print(f'[new_goto_mission]: configure job end...')

            return True
        except:
            return False

    def assign_job_CHARGING_START(self, task_json, status_callback):
        try:
            # Job START
            # TASK START
            tasks = []
            rm_map_metadata = RMSchema.TaskParams(task_json['parameters'])
            layout_guid = self.rmapi.get_layout_guid(rm_map_metadata.mapId)
            layout_marker_guid = self.rmapi.get_layout_marker_guid(layout_guid, rm_map_metadata.positionName)
            # configure task-01: create a new task
            charging = self.rmapi.task_goto(self.skill_config.get('RM-Skill', 'CHARGING'),
                                            layout_guid,
                                            layout_marker_guid,
                                            order=1,
                                            map_id=rm_map_metadata.mapId,
                                            pos_name=rm_map_metadata.positionName,
                                            x=rm_map_metadata.x,
                                            y=rm_map_metadata.y,
                                            heading=rm_map_metadata.heading)
            tasks.append(charging)
            print(charging)
            # TASK END
            print(f'[new_goto_mission]: configure task end...')

            self.rmapi.new_job(self.robot_guid, layout_guid, tasks=tasks, job_name='CHARGING-GOTO-DEMO')
            print(f'[new_goto_mission]: configure job end...')

            return True
        except:
            return False

    def charging_start(self, task_json, status_callback):
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

    def charging_stop(self, task_json, status_callback):
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

    # Follow Me
    def follow_me_mode(self, task_json):
        try:
            self.rvapi.change_mode_followme()
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


if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    skill_config_path = './conf/rm_skill.properties'

    robot = Robot(config, port_config, skill_config_path)

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
    
