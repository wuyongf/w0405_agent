import mysql.connector
import src.models.db_azure as db
import src.utils.methods as umethods
import src.models.enums.nw as NWEnums
import src.models.schema.nw as NWSchema
import src.models.schema.rm as RMSchema
import src.models.schema.rv as RVSchema


class robotDBHandler(db.AzureDB):
    # init and connect to NWDB
    def __init__(self, config):
        self.cfg = {
            'host':config.get('NWDB','host'),
            'user':config.get('NWDB','user'),
            'password':config.get('NWDB','password'),
            'database':config.get('NWDB','database'),
            'client_flags': [mysql.connector.ClientFlag.SSL],
            'ssl_ca':config.get('NWDB','ssl_ca')}
        super().__init__(self.cfg)
        self.database = config.get('NWDB','database')
        self.robot_rm_guid = config.get('NWDB','robot_rm_guid')
        self.robot_id = self.get_robot_id()
        self.nwdb_lift_id = config.get('NWDB_Lift','lift_id')
    
    def get_robot_id(self):
        statement = f'SELECT ID FROM {self.database}.`robot.status` WHERE guid = "{self.robot_rm_guid}";'
        # print(statement)
        return self.Select(statement)

    def update_robot_battery(self, battery):
        try: 
            statement = f'UPDATE {self.database}.`robot.status` SET battery = {battery} WHERE ID = {self.robot_id};'
            # print(statement)
            self.Update(statement)
        except:
            print('[db_robot.update_robot_battery] error')

    def update_robot_position(self, x, y, theta):
        try: 
            statement = f'UPDATE {self.database}.`robot.status` SET pos_x = {x}, pos_y = {y}, pos_theta = {theta},  modified_date = "{self.now()}" WHERE ID = {self.robot_id};'
            # print(statement)
            self.Update(statement)
        except:
            print('[db_robot.update_robot_position] error')

    def update_robot_map_id(self, map_id):
        if map_id is not None:
            statement = f'UPDATE {self.database}.`robot.status` SET map_id = {map_id} WHERE ID = {self.robot_id};'
        else:
            statement = f'UPDATE {self.database}.`robot.status` SET map_id = NULL WHERE ID = {self.robot_id};'
        # print(statement)
        self.Update(statement)

    def update_robot_status_mode(self, mode = NWEnums.RobotStatusMode):
        try: 
            self.update_single_value('robot.status', 'mode', mode.value, 'ID', self.robot_id)
        except:
            print('[db_robot.update_robot_status_mode] error')


    def update_robot_locker_status(self, is_closed):
        if is_closed is not None:
            statement = f'UPDATE {self.database}.`robot.status` SET locker_closed = {is_closed} WHERE ID = {self.robot_id};'
        else:
            statement = f'UPDATE {self.database}.`robot.status` SET locker_closed = NULL WHERE ID = {self.robot_id};'
        # print(statement)
        self.Update(statement)

    # map (rv and rm)
    def get_map_amr_guid(self, rm_guid):
        statement = f'SELECT amr_guid FROM {self.database}.`robot.map` WHERE rm_guid = "{rm_guid}";'
        # print(statement)
        return self.Select(statement)
    
    def get_map_rm_guid(self, amr_guid):
        statement = f'SELECT rm_guid FROM {self.database}.`robot.map` WHERE amr_guid = "{amr_guid}";'
        # print(statement)
        return self.Select(statement)
    
    def get_map_id(self, amr_guid):
        statement = f'SELECT ID FROM {self.database}.`robot.map` WHERE amr_guid = "{amr_guid}";'
        # print(statement)
        return self.Select(statement)
    
    def check_map_exist(self, amr_guid):
        statement = f'SELECT EXISTS(SELECT * from {self.database}.`robot.map` WHERE amr_guid="{amr_guid}")'
        return self.Select(statement)
    
    def check_mission_id_exist(self, mission_id):
        statement = f'SELECT EXISTS(SELECT * from {self.database}.`sys.mission` WHERE rm_mission_guid="{mission_id}")'
        return self.Select(statement)
    
    def insert_new_mission_id(self,robot_id, mission_id, type = NWEnums.MissionType.IAQ):
        statement = f'INSERT INTO {self.database}.`sys.mission` (robot_id, rm_mission_guid, created_date, type) VALUES \
                                                                ({robot_id}, "{mission_id}", "{self.now()}", {type.value})'
        return self.Insert(statement)

    def get_latest_mission_id(self):
        statement = f"SELECT LAST_INSERT_ID() FROM {self.database}.`sys.mission`"
        return self.Select(statement)
    
    # CHARGING
    def get_available_charging_station_id(self, robot_id):
        statement = f'SELECT dock_location_id FROM {self.database}.`robot.status` WHERE ID = "{robot_id}";'
        return self.Select(statement)

    def get_charing_station_detail(self, available_charging_station_id):
        # mission_id = self.nwdb.get_single_value('sys.mission.delivery', 'mission_id', 'ID', available_delivery_id)
        ID = available_charging_station_id
        # robot_id = self.get_single_value('sys.mission.delivery', 'robot_id', 'ID', ID)
        layout_nw_id = self.get_single_value('data.robot.status.dock.location', 'layout_id', 'ID', ID)
        layout_rm_guid = self.get_single_value('robot.map.layout', 'rm_guid', 'ID', layout_nw_id)
        map_id = self.get_single_value('robot.map.layout', 'activated_map_id', 'ID', layout_nw_id)
        map_rm_guid = self.get_single_value('robot.map', 'rm_guid', 'ID', map_id)
        pos_name = self.get_single_value('data.robot.status.dock.location', 'pos_name', 'ID', ID)
        pos_x = self.get_single_value('data.robot.status.dock.location', 'pos_x', 'ID', ID)
        pos_y = self.get_single_value('data.robot.status.dock.location', 'pos_y', 'ID', ID)
        pos_theta = self.get_single_value('data.robot.status.dock.location', 'pos_theta', 'ID', ID)
        
        return NWSchema.ChargingStation(layout_nw_id, layout_rm_guid, map_id, map_rm_guid, pos_name, pos_x, pos_y, pos_theta)
    
    # Lift
    def configure_lift_mission(self, cur_layout_id, target_layout_id):
        # mission_id = self.nwdb.get_single_value('sys.mission.delivery', 'mission_id', 'ID', available_delivery_id)
        lift_id = self.nwdb_lift_id
        robot_id = self.robot_id
        
        # cur_layout_id = cur_layout_id
        cur_floor_int = self.get_single_value('robot.map.layout', 'floor_id', 'ID', cur_layout_id)
        cur_waiting_pos_id = self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': cur_floor_int, 'pos_type': 'in'})[0]
        cur_transit_pos_id = self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': cur_floor_int, 'pos_type': 'transit'})[0]

        # target_layout_id = target_layout_id
        target_floor_int = self.get_single_value('robot.map.layout', 'floor_id', 'ID', target_layout_id)
        target_waiting_pos_id = self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': target_floor_int, 'pos_type': 'out'})[0]
        target_transit_pos_id = self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': target_floor_int, 'pos_type': 'transit'})[0]
        target_out_pos_id =  self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': target_floor_int, 'pos_type': 'out'})[0]

        # liftmap_layout_id
        liftmap_layout_id = 999
        liftmap_in_pos_id = self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': 999, 'pos_type': 'in'})[0]
        liftmap_transit_pos_id = self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': 999, 'pos_type': 'transit'})[0]
        liftmap_out_pos_id = self.get_value_with_conditions('data.lift.location', 'ID', {'lift_id': self.nwdb_lift_id, 'floor_id': 999, 'pos_type': 'out'})[0]
        
        return NWSchema.LiftMission(lift_id, robot_id, 
                 cur_layout_id, cur_floor_int, cur_waiting_pos_id, cur_transit_pos_id,
                 target_layout_id, target_floor_int, target_waiting_pos_id, target_transit_pos_id, target_out_pos_id,
                 liftmap_layout_id, liftmap_in_pos_id, liftmap_transit_pos_id, liftmap_out_pos_id)

    def get_lift_position_detail(self, pos_id):
        floor_id = self.get_single_value('data.lift.location', 'floor_id', 'ID', pos_id)
        layout_id = self.get_single_value('robot.map.layout', 'ID', 'floor_id', floor_id)
        layout_rm_guid = self.get_single_value('robot.map.layout', 'rm_guid', 'ID', layout_id)
        map_id = self.get_single_value('robot.map.layout', 'activated_map_id', 'ID', layout_id)
        map_rm_guid = self.get_single_value('robot.map', 'rm_guid', 'ID', map_id)
        pos_name = self.get_single_value('data.lift.location', 'pos_name', 'ID', pos_id)
        pos_x = self.get_single_value('data.lift.location', 'pos_x', 'ID', pos_id)
        pos_y = self.get_single_value('data.lift.location', 'pos_y', 'ID', pos_id)
        pos_theta = self.get_single_value('data.lift.location', 'pos_theta', 'ID', pos_id)
        
        return NWSchema.LiftPose(layout_rm_guid, map_rm_guid, pos_name, pos_x, pos_y, pos_theta)

    # DELIVERY
    def get_available_delivery_id(self):
        statement = f'SELECT ID FROM {self.database}.`sys.mission.delivery` WHERE status = 0 AND "{self.now()}" < planned_start_time;'
        return self.Select(statement)
    
    def configure_delivery_mission(self, available_delivery_id):
        # mission_id = self.nwdb.get_single_value('sys.mission.delivery', 'mission_id', 'ID', available_delivery_id)
        ID = available_delivery_id
        robot_id = self.get_single_value('sys.mission.delivery', 'robot_id', 'ID', available_delivery_id)
        sender_id = self.get_single_value('sys.mission.delivery', 'sender_id', 'ID', available_delivery_id)
        pos_origin_id = self.get_single_value('sys.mission.delivery', 'pos_origin_id', 'ID', available_delivery_id)
        receiver_id = self.get_single_value('sys.mission.delivery', 'receiver_id', 'ID', available_delivery_id)
        pos_destination_id = self.get_single_value('sys.mission.delivery', 'pos_destination_id', 'ID', available_delivery_id)

        return NWSchema.DeliveryMission(ID, robot_id, sender_id, pos_origin_id, receiver_id, pos_destination_id)
    
    def get_delivery_position_detail(self, pos_id):
        layout_id = self.get_single_value('data.sys.mission.delivery.location', 'layout_id', 'ID', pos_id)
        layout_rm_guid = self.get_single_value('robot.map.layout', 'rm_guid', 'ID', layout_id)
        map_id = self.get_single_value('robot.map.layout', 'activated_map_id', 'ID', layout_id)
        map_rm_guid = self.get_single_value('robot.map', 'rm_guid', 'ID', map_id)
        pos_name = self.get_single_value('data.sys.mission.delivery.location', 'pos_name', 'ID', pos_id)
        pos_x = self.get_single_value('data.sys.mission.delivery.location', 'pos_x', 'ID', pos_id)
        pos_y = self.get_single_value('data.sys.mission.delivery.location', 'pos_y', 'ID', pos_id)
        pos_theta = self.get_single_value('data.sys.mission.delivery.location', 'pos_theta', 'ID', pos_id)
        
        return NWSchema.DeliveryPose(layout_rm_guid, map_rm_guid, pos_name, pos_x, pos_y, pos_theta)
        # return RMSchema.mapPose(pos_layout_rm_guid, pos_x, pos_y, pos_theta)
        # pass

    def get_delivery_person_info(self, person_id):
        name_en = self.get_single_value('data.sys.mission.delivery.contact', 'name_en', 'ID', person_id)
        name_cn = self.get_single_value('data.sys.mission.delivery.contact', 'name_cn', 'ID', person_id)
        number = self.get_single_value('data.sys.mission.delivery.contact', 'number', 'ID', person_id)
        email = self.get_single_value('data.sys.mission.delivery.contact', 'email', 'ID', person_id)
        
        return NWSchema.DeliveryPerson(name_en, name_cn, number, email)


    def get_locker_command(self, id):
        statement = f'SELECT locker_command FROM {self.database}.`sys.mission.delivery` WHERE ID = {id};'
        return self.Select(statement)
    
    def update_locker_command(self, value, id):
        try: 
            statement = f'UPDATE {self.database}.`sys.mission.delivery` SET locker_command = {value} WHERE ID = {id};'
            # print(statement)
            self.Update(statement)
        except:
            print('[db_robot.update_locker_command] error')
    
    def get_delivery_status(self, id):
        statement = f'SELECT status FROM {self.database}.`sys.mission.delivery` WHERE ID = {id};'
        return self.Select(statement)
    
    def update_delivery_status(self, value, id):
        try: 
            statement = f'UPDATE {self.database}.`sys.mission.delivery` SET status = {value} WHERE ID = {id};'
            # print(statement)
            self.Update(statement)
        except:
            print('[db_robot.update_delivery_status] error')

    # BASIC METHOD
    def get_single_value(self, table, target, condition, condition_value):
        # statement = f'SELECT sender_id FROM {self.database}.`sys.mission.delivery` WHERE status = 0 AND "{self.now()}" < planned_start_time;'
        statement = f'SELECT {target} FROM {self.database}.`{table}` WHERE {condition} = {condition_value};'
        return self.Select(statement)
    
    def get_values(self, table, target, condition, condition_value):
        statement = f'SELECT {target} FROM {self.database}.`{table}` WHERE {condition} = {condition_value};'
        result = self.SelectAll(statement)
        values = [row[target] for row in result]  # Extract the values from the result rows
        return values
    
    def get_value_with_conditions(self, table, target, conditions):
        try:
            # Construct the WHERE clause for multiple conditions
            where_clause = ' AND '.join([f'{key} = \'{value}\'' for key, value in conditions.items()])
            statement = f'SELECT {target} FROM {self.database}.`{table}` WHERE {where_clause};'
            # Execute the SQL statement to retrieve the value
            result = self.SelectAll(statement)
            values = [row[target] for row in result]  # Extract the values from the result rows
            return values
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def update_single_value(self, table, target, target_value, condition, condition_value):
        try: 
            statement = f'UPDATE {self.database}.`{table}` SET {target} = {target_value} WHERE {condition} = {condition_value};'
            # print(statement)
            self.Update(statement)
        except:
            pass
            # print('[db_robot.update_single_value] error')

    # UI Handler
    def update_ui_display_status(self, ui_flag, mission_type, status):
        try: 
            statement = f'UPDATE {self.database}.`ui.display.status` SET ui_flag = {ui_flag}, mission_type = {mission_type}, status = {status} WHERE robot_id = {self.robot_id};'
            self.Update(statement)
        except:
            print('[db_robot.update_ui_display_status] error')

    def update_ui_mission_status(self, status, robot_nw_id, mission_id = None):
        # robot.status
        self.update_single_value('robot.status','mission_status',status,'ID',robot_nw_id)
        # # sys.mission
        # self.update_single_value('sys.mission','status',status,'ID',mission_id)
        pass

    def update_ui_mission_detailed_info(self, detailed_info, robot_nw_id, mission_id = None):
        # robot.status
        self.update_single_value('robot.status','mission_detailed_info',detailed_info,'ID',robot_nw_id)
        # # sys.mission
        # self.update_single_value('sys.mission','detailed_info',detailed_info,'ID',mission_id)
        pass

    # AI

    ### rgbcam
    def insert_new_video_id(self, camera_position: NWEnums.CameraPosition, robot_id, mission_id, video_file_name):
        statement = None
        if camera_position == NWEnums.CameraPosition.Front:
            statement = f'INSERT INTO {self.database}.`ai.lift_inspection.video.front` (robot_id, mission_id, video_file_name, created_date) VALUES \
                          ({robot_id}, {mission_id}, "{video_file_name}", "{self.now()}")'
        if camera_position == NWEnums.CameraPosition.Rear:
            statement = f'INSERT INTO {self.database}.`ai.lift_inspection.video.rear` (robot_id, mission_id, video_file_name, created_date) VALUES \
                          ({robot_id}, {mission_id}, "{video_file_name}", "{self.now()}")'        
        # print(statement)
        return self.Insert(statement)

    def get_latest_video_id(self, camera_position: NWEnums.CameraPosition):
        statement = None
        if camera_position == NWEnums.CameraPosition.Front:
            statement = f"SELECT LAST_INSERT_ID() FROM {self.database}.`ai.lift_inspection.video.front`"
        if camera_position == NWEnums.CameraPosition.Rear:
            statement = f"SELECT LAST_INSERT_ID() FROM {self.database}.`ai.lift_inspection.video.rear`"        
        return self.Select(statement)

    ### mic
    def insert_new_audio_id(self,robot_id, mission_id, audio_file_name, is_abnormal):
        statement = f'INSERT INTO {self.database}.`ai.lift_inspection.audio` (robot_id, mission_id, audio_file_name, is_abnormal, created_date) VALUES \
                                                                ({robot_id}, {mission_id}, "{audio_file_name}", {is_abnormal}, "{self.now()}")'
        print(f'statement: {statement}')
        return self.Insert(statement)

    def get_latest_audio_id(self):
        statement = f"SELECT LAST_INSERT_ID() FROM {self.database}.`ai.lift_inspection.audio`"
        return self.Select(statement)
    
    def insert_new_audio_analysis(self, audio_id, formatted_output_list, audio_type: NWEnums.AudioType):

        for formatted_output in formatted_output_list:
            
            formatted_output = list(formatted_output.split(','))
            order = formatted_output[0]
            start_time = formatted_output[1]
            end_time = formatted_output[2]
            slice_count = formatted_output[3]

            statement = f'INSERT INTO {self.database}.`ai.lift_inspection.audio.analysis`\
                        (audio_id, `order`, slice_count, audio_type, start_time, end_time, created_date) VALUES \
                        ({audio_id}, {order}, {slice_count}, {audio_type.value}, {start_time}, {end_time}, "{self.now()}")'
            
            print(statement)
            self.Insert(statement)
        
        return True

    ### thermal
    def insert_new_thermal_id(self,robot_id, mission_id, image_folder_name, is_abnormal):
        statement = f'INSERT INTO {self.database}.`ai.water_leakage.thermal` (robot_id, mission_id, image_folder_name, is_abnormal, created_date) VALUES \
                                                                ({robot_id}, {mission_id}, "{image_folder_name}", {is_abnormal}, "{self.now()}")'
        return self.Insert(statement) 
      
    def get_latest_thermal_id(self):
        statement = f"SELECT LAST_INSERT_ID() FROM {self.database}.`ai.water_leakage.thermal`"
        return self.Select(statement)
    
    def insert_new_thermal_analysis(self, thermal_id, image_name, is_abnormal, layout_id, robot_x, robot_y, created_date):

        statement = f'INSERT INTO {self.database}.`ai.water_leakage.thermal.analysis`\
                    (thermal_id, `image_name`, is_abnormal, layout_id, robot_x, robot_y, created_date) VALUES \
                    ({thermal_id}, "{image_name}", {is_abnormal}, {layout_id}, {robot_x}, {robot_y}, "{created_date}")'
        
        print(statement)
        return self.Insert(statement)
    
    ### lift_inspection
    def insert_lift_inspection_info(self, mission_id, raw_audio_dir, raw_video_front_dir, raw_video_rear_dir,
                                     temp_dir, preprocess_dir):
            
        statement = f'INSERT INTO {self.database}.`ai.lift_inspection.task_info`\
                    (ID, raw_audio_dir, raw_video_front_dir, raw_video_rear_dir, temp_dir, preprocess_dir) VALUES \
                    ({mission_id}, "{raw_audio_dir}", "{raw_video_front_dir}", "{raw_video_rear_dir}", "{temp_dir}", "{preprocess_dir}")'
        
        print(statement)
        self.Insert(statement)
        
        return True
if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)

    # from src.models.schema.nw import Door    
    # nwdb.update_robot_status_mode(NWEnums.RobotStatusMode.Error)

    ### Lift
    # base64 = nwdb.get_single_value('robot.map.layout', 'base64', 'name', "'GF-Layout'")

    ### ui_mission_status
    nwdb.update_ui_mission_detailed_info(detailed_info=6,robot_nw_id=1)

    # ### Update base64
    # text_file = open("sample.txt", "r")
    # data = text_file.read()
    # nwdb.update_single_value('robot.map', 'base64', f"'{data}'", 'ID', 7)

    # ### Lift
    # target_layout_id = nwdb.get_single_value('robot.map', 'layout_id', 'rm_guid', "'d6734e98-f53a-4b69-8ed8-cbc42ef58e3a'")
    # print(target_layout_id)

    # a_lift_mission = nwdb.configure_lift_mission(5,6)
    # print(a_lift_mission)

    # lift_pos = nwdb.get_lift_position_detail(1)
    # print(lift_pos)

    # # door
    # doors = nwdb.get_value_with_conditions('nw.event.region', 'polygon', {'layout_id': 5, 'is_door': 1})
    # for door in doors:
    #     print(door)

    # # charging status
    # id = nwdb.get_available_charging_station_id(1)
    # charging_station_detail = nwdb.get_charing_station_detail(id)
    # print(charging_station_detail.to_json())

    # # doors
    # result = nwdb.get_values('data.robot.map.layout.door.location', 'ID', 'layout_id', 3)
    # print(result)

    # layout_id = 3
    # # get door_ids from NWDB
    # door_ids =  nwdb.get_values('data.robot.map.layout.door.location', 'ID', 'layout_id', layout_id)
    
    # # Assume door_ids is a list of door IDs retrieved from the database
    # door_list = []
    # for door_id in door_ids:
    #     # Fetch the remaining properties from the database based on the door ID
    #     layout_id = nwdb.get_single_value('data.robot.map.layout.door.location', 'layout_id', 'ID', door_id)
    #     name = nwdb.get_single_value('data.robot.map.layout.door.location', 'name', 'ID', door_id)
    #     pos_x = nwdb.get_single_value('data.robot.map.layout.door.location', 'pos_x', 'ID', door_id)
    #     pos_y = nwdb.get_single_value('data.robot.map.layout.door.location', 'pos_y', 'ID', door_id)
    #     pos_heading = nwdb.get_single_value('data.robot.map.layout.door.location', 'pos_heading', 'ID', door_id)
    #     # Create a Door object and append it to the list
    #     door = Door(layout_id, name, pos_x, pos_y, pos_heading)
    #     door_list.append(door)

    # print(door_list[0])

    # position
    # json = {'robotId': 'RV-ROBOT-SIMULATOR', 'mapName': '', 'x': 13.0, 'y': 6.6, 'angle': 0.31}
    # nwdb.update_robot_position(13,12,210)

    # # battery
    # nwdb.UpdateRobotBattery(12.22)

    # # map
    # res = nwdb.get_map_amr_guid('56ded5f9-79a3-458e-8458-8a76e818048e')
    # print(res)

    # mission_id: 9b73504f-b4de-4a75-98c8-468cf588c5f6
    # nwdb.insert_new_mission_id(1, '9b73504f-b4de-4a75-98c8-468cf588c5f0', NWEnums.MissionType.IAQ)
    # res = nwdb.check_mission_id_exist('')
    # print(res)

    # id = nwdb.get_latest_mission_id()
    # print(id)

    # # delivery
    # id = nwdb.get_available_delivery_id()
    # print(id)
    # nwdb.update_ui_display_status( ui_flag=1, mission_type=2, status=5)

    # sender_id = nwdb.get_single_value('sys.mission.delivery', 'sender_id', 'ID', id)
    # print(sender_id)
