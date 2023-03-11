import mysql.connector
import src.models.db_azure as db
from jproperties import Properties  # config file
import useful_functions.methods as um

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
        self.robot_guid = config.get('NWDB','robot_guid')
        self.database = config.get('NWDB','database')

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
        print(statement)
        res = self.FetchOne(statement)

    def UpdateRobotBattery(self, robot_id, battery):
        pass
    def UpdateRobotPosition(self, robot_id, pos):
        pass
    def UpdateRobotMissionStatus(self, robot_id, mission_status):
        pass
    def UpdateDemo(self):
        quantity = 333
        id = 8
        statement3 = f'UPDATE inventory SET quantity = {quantity} WHERE id = {id};'
        self.Query(statement3)

if __name__ == '__main__':
    config = um.load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)
    nwdb.GetRobotId()
    pass