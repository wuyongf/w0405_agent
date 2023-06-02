import mysql.connector
import src.models.db_azure as db
import src.utils.methods as umethods
import src.models.schema.rv as RVSchema
import src.models.enums.nw as NWEnums

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
            statement = f'UPDATE {self.database}.`robot.status` SET pos_x = {x}, pos_y = {y}, pos_theta = {theta},  modified_date = now() WHERE ID = {self.robot_id};'
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

    def update_robot_mission_status(self, mission_status):
        pass

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
    
    def insert_new_mission_id(self,robot_id, mission_id, type = NWEnums.MissionType):
        statement = f'INSERT INTO {self.database}.`sys.mission` (robot_id, rm_mission_guid, created_date, type) VALUES \
                                                                ({robot_id}, "{mission_id}", now(), {type.value})'
        return self.Insert(statement)

    def get_latest_mission_id(self):
        statement = f"SELECT LAST_INSERT_ID() FROM {self.database}.`sys.mission`"
        return self.Select(statement)

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)

    # # position
    # json = {'robotId': 'RV-ROBOT-SIMULATOR', 'mapName': '', 'x': 13.0, 'y': 6.6, 'angle': 0.31}
    # nwdb.UpdateRobotPosition(RVSchema.Pose(json))

    # # battery
    # nwdb.UpdateRobotBattery(12.22)

    # # map
    # res = nwdb.get_map_amr_guid('56ded5f9-79a3-458e-8458-8a76e818048e')
    # print(res)

    # mission_id: 9b73504f-b4de-4a75-98c8-468cf588c5f6
    nwdb.insert_new_mission_id('9b73504f-b4de-4a75-98c8-468cf588c5f9', NWEnums.MissionType.IAQ)
    res = nwdb.check_mission_id_exist('')
    print(res)

    id = nwdb.get_latest_mission_id()
    print(id)
