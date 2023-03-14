import mysql.connector
import src.models.db_azure as db
import src.utils.methods as umethods
import src.models.schema_rv as RVSchema

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
        self.robot_id = self.GetRobotId()

    def __load_config(self, config_addr):
        # Load config file
        configs = Properties()
        try:
            with open(config_addr, 'rb') as config_file:
                configs.load(config_file)
        except:
            print("[robotDBHandler]: Error loading properties file, check the correct directory")
        return configs
    
    def GetRobotId(self):
        statement = f'SELECT ID FROM {self.database}.`robot.status` WHERE guid = "{self.robot_guid}";'
        # print(statement)
        return self.Select(statement)

    def UpdateRobotBattery(self, battery):
        statement = f'UPDATE {self.database}.`robot.status` SET battery = {battery} WHERE ID = {self.robot_id};'
        # print(statement)
        self.Update(statement)

    def UpdateRobotPosition(self, x, y, theta):
        statement = f'UPDATE {self.database}.`robot.status` SET pos_x = {x}, pos_y = {y}, pos_theta = {theta} WHERE ID = {self.robot_id};'
        # print(statement)
        self.Update(statement)

    def UpdateRobotMissionStatus(self, mission_status):
        pass

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)

    # # position
    # json = {'robotId': 'RV-ROBOT-SIMULATOR', 'mapName': '', 'x': 13.0, 'y': 6.6, 'angle': 0.31}
    # nwdb.UpdateRobotPosition(RVSchema.Pose(json))

    # # battery
    nwdb.UpdateRobotBattery(12.22)
    pass