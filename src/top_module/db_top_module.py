import time
import json
import mysql.connector
import src.models.db_azure as db
import src.utils.methods as umethods
import src.models.robot as Robot
import src.models.enums.nw as NWEnum
import datetime


class TopModuleDBHandler(db.AzureDB):
    # init and connect to NWDB
    def __init__(self, config, status_summary):
        self.cfg = {
            'host': config.get('NWDB', 'host'),
            'user': config.get('NWDB', 'user'),
            'password': config.get('NWDB', 'password'),
            'database': config.get('NWDB', 'database'),
            'client_flags': [mysql.connector.ClientFlag.SSL],
            'ssl_ca': config.get('NWDB', 'ssl_ca')
        }
        super().__init__(self.cfg)
        self.database = config.get('NWDB', 'database')
        self.status_summary = status_summary
        self.robot_guid = config.get('NWDB', 'robot_rm_guid')
        self.robot_id = self.GetRobotId()

    def get_robot_summary(self):
        # (pos_x, pos_y, pos_theta, map_id, map_rm_guid) = self.get_robot_summary()

        obj = json.loads(self.status_summary())
        pos_x = obj["position"]["x"]
        pos_y = obj["position"]["y"]
        pos_theta = obj["position"]["theta"]
        map_id = obj["map_id"]
        map_rm_guid = obj["map_rm_guid"]
        return (pos_x, pos_y, pos_theta, map_id, map_rm_guid)

    def GetRobotId(self):
        statement = f'SELECT ID FROM {self.database}.`robot.status` WHERE guid = "{self.robot_guid}";'
        return self.Select(statement)

    def GetLayoutIdByMapId(self, map_id):
        statement = f'SELECT layout_id FROM {self.database}.`robot.map` WHERE ID = {map_id};'
        return self.Select(statement)

    def StreamIaqData(self, table, key, value):
        statement = f'insert into {self.database}.`{table}` ({", ".join(map(str, key))}, created_date, robot_id) VALUES ({", ".join(map(str, value))}, "{self.now()}", {self.robot_id});'
        # print(f'[db_top_module.StreamIaqData]: {statement}')
        self.Insert(statement)

    def DeleteLastStreamIaqData(self):
        statement = f'delete from {self.database}.`sensor.iaq.stream` WHERE robot_id = {self.robot_id} ORDER BY ID ASC LIMIT 1 ;'
        # print(f'[db_top_module.StreamIaqData]: {statement}')
        self.Delete(statement)

    def InsertIaqData(self, table, key, value, task_id):
        # map_name
        # task_id
        # posX,Y
        statement = f'insert into {self.database}.`{table}` ({", ".join(map(str, key))}, created_date, task_id, robot_id) VALUES ({", ".join(map(str, value))}, "{self.now()}", {task_id}, {self.robot_id});'
        print(f'[db_top_module.InsertIaqData]: {statement}')
        self.Insert(statement)

    def GetIaqData(self, task_id):
        statement = f'SELECT * FROM {self.database}.`sensor.iaq.history` WHERE task_id = {task_id}'
        return self.SelectAll(statement)

    def GetUserRules(self):
        # TODO *** Let the userrules get sensor type from table "data.sensor.type"
        statement = f'SELECT u.*, t.data_type FROM {self.database}.`nw.event.user_rules` u JOIN {self.database}.`data.sensor.type` t ON u.data_type_fk = t.ID;'
        print("Get user rules")
        return self.SelectAll(statement)

    def GetRegions(self):
        statement = f'SELECT ID, name, polygon, layout_id FROM {self.database}.`nw.event.region`;'
        return self.SelectAll(statement)

    def GetRegionsByMapId(self, map_id: int):
        statement = f'SELECT u.ID, u.name, u.polygon, u.layout_id FROM {self.database}.`nw.event.region` u JOIN {self.database}.`robot.map` v ON u.layout_id = v.layout_id WHERE v.ID = {map_id};'
        return self.SelectAll(statement)

    def GetRegionsByLayoutId(self, layout_id: int):
        statement = f'SELECT u.ID, u.name, u.polygon, FROM {self.database}.`nw.event.region` u WHERE u.layout_id = {layout_id};'
        return self.SelectAll(statement)

    def InsertEventLog(self, task_id, data_type, rule_name, severity, rule_threshold, pos_x, pos_y, layout_id,
                       event_id):
        statement = f'insert into {self.database}.`nw.event.log` (task_id, data_type, rule_name, severity, rule_threshold, pos_x, pos_y, layout_id, created_date, event_id) VALUES ({task_id}, "{data_type}", "{rule_name}", {severity}, {rule_threshold}, {pos_x}, {pos_y}, {layout_id}, "{self.now()}", "{event_id}");'
        print(f'[db_top_module.InsertEventLog]: {statement}')
        self.Insert(statement)

    def CreateDistanceDataPack(self, task_id):
        # pos_x
        # pos_y
        # floor_id
        (pos_x, pos_y, pos_theta, map_id, map_rm_guid) = self.get_robot_summary()
        # statement = f'INSERT INTO {self.database}.`sensor.distance_sensor.datapack` (task_id, created_date, robot_id, pos_x, pos_y, pos_theta, map_id) VALUES ("{task_id}", now(), {self.robot_id}, {pos_x}, {pos_y}, {pos_theta}, {map_id})'
        statement = f'INSERT INTO {self.database}.`sensor.distance_sensor.datapack` (task_id, created_date, robot_id, pos_x, pos_y, pos_theta, map_id) VALUES ("{task_id}", "{self.now()}", {self.robot_id}, {pos_x}, {pos_y}, {pos_theta}, {map_id})'
        self.Insert(statement)
        # return the auto-generated ID of the new data pack
        return self.Select("SELECT LAST_INSERT_ID()")

    def UpdateDistanceResult(self, column: str, id: int, result: float):
        statement = f'UPDATE {self.database}.`sensor.distance_sensor.datapack` SET {column} = "{result}" WHERE id = {id}'
        self.Insert(statement)

    def InsertDistanceChunk(self, pack_id, distance_chunk_left, distance_chunk_right, move_dir):
        statement = f'INSERT INTO {self.database}.`sensor.distance_sensor.datachunk` (pack_id, distance_chunk_left, distance_chunk_right, move_dir, created_date, robot_id) VALUES ("{pack_id}", "{distance_chunk_left}", "{distance_chunk_right}", "{move_dir}" , "{self.now()}", {self.robot_id})'
        self.Insert(statement)

    # Get raw data set of laser distance chunk
    def GetDistanceChunk(self, side, pack_id, move_dir):
        statement = f'SELECT `distance_chunk_{side}` FROM {self.database}.`sensor.distance_sensor.datachunk` WHERE pack_id = "{pack_id}" AND move_dir = "{move_dir}";'
        return self.SelectAll(statement)

    # Get laser distance list
    def GetDistanceResult(self, side, pack_id, move_dir):
        result = []
        for i in self.GetDistanceChunk(side=side, pack_id=pack_id, move_dir=move_dir):
            result = result + list(i.values())[0].split(",")
        return result

    # Create Gyro Data Pack
    def CreateGyroDataPack(self, task_id, lift_id):
        # pos_x
        # pos_y
        # floor_id
        (pos_x, pos_y, pos_theta, map_id, map_rm_guid) = self.get_robot_summary()
        statement = f'INSERT INTO {self.database}.`sensor.gyro.datapack` (task_id, created_date, robot_id, lift_id, pos_x, pos_y, pos_theta, map_id) VALUES ("{task_id}", "{self.now()}", {self.robot_id}, {lift_id}, {pos_x}, {pos_y}, {pos_theta}, {map_id})'
        self.Insert(statement)
        # return the auto-generated ID of the new data pack
        return self.Select("SELECT LAST_INSERT_ID()")

    # Insert Gyro Data Chunk
    def InsertGyroChunk(self, pack_id, accel_z):
        statement = f'INSERT INTO {self.database}.`sensor.gyro.datachunk` (pack_id, accel_z, created_date) VALUES ("{pack_id}", "{accel_z}", "{self.now()}")'
        self.Insert(statement)

    # Get raw data set of gyro chunk
    def GetGyroChunk(self, pack_id):
        statement = f'SELECT `accel_z` FROM {self.database}.`sensor.gyro.datachunk` WHERE pack_id = "{pack_id}"'
        return self.SelectAll(statement)

    # Get Gyro data list
    def GetGyroResult(self, pack_id):
        result = []
        for i in self.GetGyroChunk(pack_id=pack_id):
            result = result + list(i.values())[0].split(",")
        return result

    def UpdateGyroResult(self, column: str, id: int, result: str, result_min, result_max):
        statement = f'UPDATE {self.database}.`sensor.gyro.datapack` SET {column} = "{result}" , result_min = {result_min}, result_max = {result_max} WHERE id = {id}'
        self.Insert(statement)

    def GetHeatmap(self, task_id, data_type):
        statement = f'SELECT * FROM {self.database}.`nw.event.heatmap` WHERE `task_id` = "{task_id}" AND `data_type` = "{data_type}"'
        return self.SelectAll(statement)[0] if self.SelectAll(statement) else None

    def InsertHeatmap(self, task_id, mesh_size, data_type, x_grid_min, x_grid_max, y_grid_min, y_grid_max, data_list):
        statement = f'INSERT INTO {self.database}.`nw.event.heatmap` (task_id, mesh_size, data_type, x_grid_min, x_grid_max, y_grid_min, y_grid_max, data_list) VALUES ("{task_id}", "{mesh_size}", "{data_type}", "{x_grid_min}" , "{x_grid_max}", "{y_grid_min}", "{y_grid_max}", "{data_list}")'
        self.Insert(statement)

    def InsertHeatmapComparison(self, task_id, target_task_id, mission_guid, data_type, delta_data_list, max_delta, mean_delta):
        statement = f'INSERT INTO {self.database}.`nw.event.heatmap.comparison` (task_id, target_task_id, mission_guid, data_type, delta_data_list, max_delta, mean_delta) VALUES ("{task_id}", "{target_task_id}", "{mission_guid}", "{data_type}" , "{delta_data_list}", "{max_delta}", "{mean_delta}")'
        self.Insert(statement)

    def GetMissionGuidByTaskId(self, task_id):
        statement = f'SELECT `rm_mission_guid` FROM {self.database}.`sys.mission` WHERE `ID` = "{task_id}"'
        return self.Select(statement)

    def GetTaskIdListByMissionId(self, mission_guid, limit):
        # mission_guid = self.GetMissionGuid(task_id)
        statement = f'SELECT `ID` FROM {self.database}.`sys.mission` WHERE `rm_mission_guid` = "{mission_guid}" ORDER BY `ID` DESC LIMIT {limit + 2}'
        dict_list = self.SelectAll(statement)
        result = []
        for i in dict_list:
            result.append(i['ID'])
        return result

    # Get rules by task_id
    def GetHeatmapComparisonRules(self, task_id, data_type):
        mission_guid = self.GetMissionGuidByTaskId(task_id)
        statement = f'SELECT * FROM {self.database}.`nw.event.heatmap.rules` WHERE `mission_guid` = "{mission_guid}" AND `data_type` = "{data_type}"'
        result = self.SelectAll(statement)
        if len(result) > 0:
            return result[0]
        return {}

    def GetComparisonHistoryHeatmapByTaskId(self, task_id, data_type):
        comparison = self.GetHeatmapComparisonRules(task_id, data_type)
        # print(comparison)
        missionId = comparison['mission_guid']
        comparisonRange = comparison['comparison_range']
        # history mission data list
        return (self.GetHeatmapByMissionId(missionId, data_type, comparisonRange))

    def GetHeatmapByMissionId(self, mission_guid, data_type, comparison_range):
        task_id_list = self.GetTaskIdListByMissionId(mission_guid, comparison_range)
        # print("[db_top_module.py] task_id_list : ", task_id_list)
        result = []
        for i in task_id_list:
            statement = f'SELECT * FROM {self.database}.`nw.event.heatmap` WHERE `task_id` = "{i}" AND `data_type` = "{data_type}"'
            data = self.SelectAll(statement)
            if len(data) > 0:
                result.append(data[0])
        return result

    def GetTaskIdList(self, task_id, data_type):
        comparison = self.GetHeatmapComparisonRules(task_id, data_type)
        missionId = comparison['mission_guid']
        comparisonRange = comparison['comparison_range']
        task_id_list = self.GetTaskIdListByMissionId(missionId, comparisonRange)
        return task_id_list

    # def GetTaskIdList(self, mission_guid, data_type, comparison_range):
    #     task_id_list = self.GetTaskIdListByMissionId(mission_guid, comparison_range)
    #     return task_id_list

    # Third Party Sensor (Mi Air Quality Sensor 2)
    def insert_mi_sensor_data(self, table, keys, values):
        statement = f'insert into {self.database}.`{table}` ({", ".join(map(str, keys))}, created_date) VALUES ({", ".join(map(str, values))}, "{self.now()}");'
        self.Insert(statement)


if __name__ == '__main__':

    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 105.40159891291846, "y": 67.38314149752657, "theta": 75.20575899303867}, "map_id": 2, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status

    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')

    nwdb = TopModuleDBHandler(config, status_summary)

    # nwdb.CreateGyroDataPack(1,1)
    # nwdb.InsertGyroChunk(pack_id=2, accel_z=9)

    # nwdb.InsertEventLog( 999, 2, 'rule_name', 2, 1000, 1.0, 2.0, 5, "0000-0000")
    # print(nwdb.GetIaqData(199))

    # print(nwdb.GetMissionGuid(199))

    # ============================
    # comparison = nwdb.GetHeatmapComparisonRules(214, 'lux')
    # print(comparison)
    # missionId = comparison['mission_guid']
    # comparisonRange = comparison['comparison_range']
    # # history mission data list
    # print(nwdb.GetHeatmapByMissionId(missionId, 'lux', comparisonRange))
    print(nwdb.GetTaskIdList(211, 'lux'))
    # ============================

    # print(nwdb.GetTaskIdListByMissionId('5277d6a2-1f85-4587-a8b8-a6336985eca3'))

    # print(nwdb.GetHeatmap(212, 'lux'))

    # print(nwdb.GetRegions())

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
    # nwdb.Test()

    # print(nwdb.GetDistanceChunk(pack_id=65, side='left', move_dir=2))
    # print(nwdb.GetGyroResult(21))
    # nwdb.UpdateGyroResult(id=21, column='result_denoise', result='test')

    # nwdb.UpdateDistanceResult(column="result_rl", id=73, result=1)
    # nwdb.DeleteLastStreamIaqData()
