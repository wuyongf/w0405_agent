import time
import mysql.connector
import src.models.db_azure as db
import src.utils.methods as umethods
import src.models.robot as Robot
import src.models.enums.nw as NWEnum
import datetime


class TopModuleDBHandler(db.AzureDB):
    # init and connect to NWDB
    def __init__(self, config, port_config):
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

    def GetRobotId(self):
        statement = f'SELECT ID FROM {self.database}.`robot.status` WHERE guid = "{self.robot_guid}";'
        return self.Select(statement)

    def StreamIaqData(self, table, key, value):
        statement = f'insert into {self.database}.`{table}` ({", ".join(map(str, key))}, created_date, robot_id) VALUES ({", ".join(map(str, value))}, now(), {self.robot_id});'
        print(statement)
        self.Insert(statement)

    def InsertIaqData(self, table, key, value, task_id):
        # map_name
        # task_id
        # posX,Y
        statement = f'insert into {self.database}.`{table}` ({", ".join(map(str, key))}, created_date, task_id, robot_id) VALUES ({", ".join(map(str, value))}, now(), {task_id}, {self.robot_id});'
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
        statement = f'INSERT INTO {self.database}.`sensor.distance_sensor.datapack` (task_id, created_date) VALUES ("{task_id}", now())'
        self.Insert(statement)
        # return the auto-generated ID of the new data pack
        return self.Select("SELECT LAST_INSERT_ID()")

    def InsertDistanceChunk(self, pack_id, distance_chunk_left, distance_chunk_right, move_dir):
        statement = f'INSERT INTO {self.database}.`sensor.distance_sensor.datachunk` (pack_id, distance_chunk_left, distance_chunk_right, move_dir, created_date, robot_id) VALUES ("{pack_id}", "{distance_chunk_left}", "{distance_chunk_right}", "{move_dir}" , now(), {self.robot_id})'
        self.Insert(statement)

    # Get raw data set of laser distance chunk
    def GetDistanceChunk(self, side, pack_id, move_dir):
        statement = f'SELECT `distance_chunk_{side}` FROM {self.database}.`sensor.distance_sensor.datachunk` WHERE pack_id = "{pack_id}" AND move_dir = "{move_dir}";'
        return self.SelectAll(statement)

    # Get combined list of result
    def GetDistanceResult(self, side, pack_id, move_dir):
        result = []
        for i in nwdb.GetDistanceChunk(side=side, pack_id=pack_id, move_dir=move_dir):
            result = result + list(i.values())[0].split(",")
        return result

    # Create Gyro Data Pack
    def CreateDistanceDataPack(self, task_id):
        # pos_x
        # pos_y
        # floor_id
        statement = f'INSERT INTO {self.database}.`sensor.gyro.datapack` (task_id, created_date, robot_id) VALUES ("{task_id}", now(), {self.robot_id})'
        self.Insert(statement)
        # return the auto-generated ID of the new data pack
        return self.Select("SELECT LAST_INSERT_ID()")

    # Insert Gyro Data Chunk
    def InsertGyroChunk(self, pack_id, accel_z):
        statement = f'INSERT INTO {self.database}.`sensor.gyro.datachunk` (pack_id, accel_z, created_date) VALUES ("{pack_id}", "{accel_z}", now())'
        self.Insert(statement)


if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    nwdb = TopModuleDBHandler(config)
    # print(nwdb.GetUserRules_Column())
    # print(nwdb.GetUserRules())
    # print((nwdb.GetUserRules()[2]).get('type'))
    # test = [i.get('type') for i in nwdb.GetUserRules()]
    # print(test)

    # # position
    # json = {'robotId': 'RV-ROBOT-SIMULATOR', 'mapName': '', 'x': 13.0, 'y': 6.6, 'angle': 0.31}
    # nwdb.UpdateRobotPosition(RVSchema.Pose(json))

    # # battery
    # nwdb.UpdateRobotBattery(30.22)
    # nwdb.InsertIaqData("sensor.iaq.history", ["temperature", "RH", "HCHO"], [2, 3, 20], 1, 2)

    # nwdb.InsertDistanceChunk(10,"test",'test', 1)
    # print(nwdb.CreateDistanceDataPack(0))

    # print(nwdb.GetDistanceResult(side = 'left', pack_id = 50, move_dir = 2))
    nwdb.Test()

    pass
