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
        self.robot_guid = config.get('NWDB','robot_guid')
        self.robot_id = self.get_robot_id()
    
    def get_robot_id(self):
        statement = f'SELECT ID FROM {self.database}.`robot.status` WHERE guid = "{self.robot_guid}";'
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


if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)

    from src.models.schema.nw import Door
    
    nwdb.update_robot_status_mode(NWEnums.RobotStatusMode.Error)

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
