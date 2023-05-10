import time
import mysql.connector
import src.models.db_azure as db
import src.utils.methods as umethods

import datetime


class robotDBHandler(db.AzureDB):
    # init and connect to NWDB
    def __init__(self, config):
        self.cfg = {
            'host': config.get('NWDB', 'host'),
            'user': config.get('NWDB', 'user'),
            'password': config.get('NWDB', 'password'),
            'database': config.get('NWDB', 'database'),
            'client_flags': [mysql.connector.ClientFlag.SSL],
            'ssl_ca': config.get('NWDB', 'ssl_ca')}
        super().__init__(self.cfg)
        self.database = config.get('NWDB', 'database')
        self.robot_guid = config.get('NWDB', 'robot_guid')
        self.robot_id = self.GetRobotId()

    # def __load_config(self, config_addr):
    #     # Load config file
    #     configs = Properties()
    #     try:
    #         with open(config_addr, 'rb') as config_file:
    #             configs.load(config_file)
    #     except:
    #         print("[robotDBHandler]: Error loading properties file, check the correct directory")
    #     return configs

    def GetRobotId(self):
        statement = f'SELECT ID FROM {self.database}.`robot.status` WHERE guid = "{self.robot_guid}";'
        # print(statement)
        return self.Select(statement)

    def InsertIaqData(self, table, key, value):
        # map_name
        # task_id
        # posX,Y
        statement = f'insert into {self.database}.`{table}` ({", ".join(map(str, key))}, created_date) VALUES ({", ".join(map(str, value))}, now());'
        print(statement)
        self.Insert(statement)

    def GetUserRules(self):
        # TODO *** Let the userrules get sensor type from table "data.sensor.type"
        statement = f'SELECT u.*, t.data_type FROM {self.database}.`nw.event.user_rules` u JOIN {self.database}.`data.sensor.type` t ON u.data_type_fk = t.ID;'
        print("Get user rules")
        return self.SelectAll(statement)
            
    def CreateDistanceDataPack(self, task_id):
        # pos_x
        # pos_y
        # floor_id
        statement = f'INSERT INTO {self.database}.`sensor.distance_sensor` (task_id, created_date) VALUES ("{task_id}", now())'
        self.Insert(statement)
        # return the auto-generated ID of the new data pack
        return self.Select("SELECT LAST_INSERT_ID()")
        
    def InsertDistanceChunk(self, pack_id, distance_chunk_left, distance_chunk_right, move_dir ):
        statement = f'INSERT INTO {self.database}.`sensor.distance_sensor_datachunk` (pack_id, distance_chunk_left, distance_chunk_right, move_dir, created_date) VALUES ("{pack_id}", "{distance_chunk_left}", "{distance_chunk_right}", "{move_dir}" , now())'
        self.Insert(statement)


if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)
    # print(nwdb.GetUserRules_Column())
    # print(nwdb.GetUserRules())
    # print((nwdb.GetUserRules()[2]).get('type'))
    test = [i.get('type') for i in nwdb.GetUserRules()]
    # print(test)

    # # position
    # json = {'robotId': 'RV-ROBOT-SIMULATOR', 'mapName': '', 'x': 13.0, 'y': 6.6, 'angle': 0.31}
    # nwdb.UpdateRobotPosition(RVSchema.Pose(json))

    # # battery
    # nwdb.UpdateRobotBattery(30.22)
    # nwdb.InsertIaqData("sensor.iaq.history", ["temperature", "RH", "HCHO"], [2, 3, 20], 1, 2)
    
    nwdb.InsertDistanceChunk(10,"test",'test', 1,1)
    # print(nwdb.CreateDistanceDataPack(0))
    
    pass
