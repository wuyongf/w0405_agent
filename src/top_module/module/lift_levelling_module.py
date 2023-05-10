import src.top_module.io_module.linear_actuator as LinearActuator
import src.top_module.sensor.laser_distance_module as LaserDistanceSensor
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import src.top_module.enums.enums_linear_actuator as LAEnum
import src.top_module.enums.enums_laser_distance as LDEnum
import time

class LiftLevellingModule():
    def __init__(self):
        self.COM_linear_actuator = 'COM6'
        self.COM_laser_distance_left = 'COM1'
        self.COM_laser_distance_right = 'COM1'
        self.config = umethods.load_config('../../../conf/config.properties')
        self.nwdb = NWDB.robotDBHandler(self.config)
        self.laser_distance = LaserDistanceSensor.LaserDistanceSensor()
        self.cb_dir = self.callback_direction
        self.cb_finish = self.callback_finish
        self.linear_actuator = LinearActuator.LinearActuator(self.COM_linear_actuator, self.cb_dir, self.cb_finish)
        self.pack_id = 0
        
        
    def callback_direction(self):
        # called when linear acturator finish extent
        self.laser_distance.set_interrupt_flag(True)
        print("callback: change direction")
        time.sleep(2)
        # self.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Retract.value)
        # print(f"direction indicator set, move_dir = {ll.laser_distance.move_dir}")
        
        # Callback function when linear actuator finish extent,
        # 1. stop collecting data and upload immediately
        # 2. change move_dir
        # 3. get move_dir
        # 4. collect data again

        # stop insert data
        
    def callback_finish(self):
        # called when linear acturator finish retract
        print("callback: finish")
        self.laser_distance.stop()
        # self.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
        

    def start(self):
        pass
    
if __name__ == "__main__":
    ll = LiftLevellingModule()
    # ll.pack_id = ll.create_data_pack(task_id=0)
    
    # Create data pack
    ll.laser_distance.set_pack_id(ll.laser_distance.create_data_pack(task_id=1)) 
    print(f"pack created, pack_id = {ll.laser_distance.pack_id}")
    
    # Set moving direction
    ll.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
    print(f"direction indicator set, move_dir = {ll.laser_distance.move_dir}")
    
    # Start laser distance Thread
    ll.laser_distance.start()
    
    # Set time limit of extend/ retract movement
    ll.linear_actuator.set_time_limit(20.0)
    
    # Start linear actuator Thread
    ll.linear_actuator.start()
    