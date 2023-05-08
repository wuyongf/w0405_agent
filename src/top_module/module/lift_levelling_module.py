import src.top_module.io_module.linear_actuator as LinearActuator
import src.top_module.sensor.laser_distance_module as LaserDistanceSensor
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import src.top_module.enums.enums_linear_actuator as LAEnum
import src.top_module.enums.enums_laser_distance as LDEnum

class LiftLevellingModule():
    def __init__(self):
        self.COM_linear_actuator = 'COM6'
        self.COM_laser_distance_left = 'COM1'
        self.COM_laser_distance_right = 'COM1'
        self.config = umethods.load_config('../../../conf/config.properties')
        self.nwdb = NWDB.robotDBHandler(self.config)
        self.linear_actuator = LinearActuator.LinearActuator(self.COM_linear_actuator)
        self.laser_distance = LaserDistanceSensor.LaserDistanceSensor()
        self.pack_id = 0

    def create_data_pack(self, task_id):
        return self.nwdb.CreateDistanceDataPack(task_id)

    def start(self):
        pass
    
if __name__ == "__main__":
    ll = LiftLevellingModule()
    ll.pack_id = ll.create_data_pack(task_id=0)
    print(f"pack{ll.pack_id}")
    ll.laser_distance.store_data(pack_id = ll.pack_id, current_ser = LDEnum.LaserDistanceSide.Left.value, move_dir=LAEnum.LinearActuatorStatus.Extend.value)
    # ll.laser_distance.data_integration()