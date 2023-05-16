import src.top_module.io_module.linear_actuator as LinearActuator
import src.top_module.sensor.laser_distance_module as LaserDistanceSensor
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import src.top_module.enums.enums_linear_actuator as LAEnum
import src.top_module.enums.enums_laser_distance as LDEnum
import src.top_module.enums.enums_module_status as MoEnum
import time

class LiftLevellingModule():
    def __init__(self, config, port_config):
        self.nwdb = NWDB.robotDBHandler(config)
        self.laser_distance = LaserDistanceSensor.LaserDistanceSensor(config, port_config)
        self.cb_dir = self.callback_direction
        self.cb_finish = self.callback_finish
        self.linear_actuator = LinearActuator.LinearActuator(port_config, self.cb_dir, self.cb_finish)
        self.pack_id = 0
        self.status = MoEnum.LiftLevellingStatus.Idle
        
    def thread_get_status(self):
        while(True):
            print(self.status)
            time.sleep(1)

    def get_status(self):
        return self.status
        
    def callback_direction(self):
        # called when linear acturator finish extent
        self.laser_distance.set_retract_flag(True)
        print("callback: change direction")
        time.sleep(2)

        # Callback function when linear actuator finish extent,
        # 1. stop collecting data and upload immediately
        # 2. change move_dir
        # 3. get move_dir
        # 4. collect data again

        
    def callback_finish(self):
        # called when linear acturator finish retract
        print("callback: finish")
        self.laser_distance.stop()
        self.status = MoEnum.LiftLevellingStatus.Finish
        # self.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
        

    def start(self):
        self.status = MoEnum.LiftLevellingStatus.Executing

        # Create data pack
        self.laser_distance.set_pack_id(self.laser_distance.create_data_pack(task_id=1))
        print(f"pack created, pack_id = {self.laser_distance.pack_id}")
        
        # Set moving direction
        self.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
        print(f"direction indicator set, move_dir = {self.laser_distance.move_dir}")
        
        # Start laser distance Thread
        self.laser_distance.start()
        
        # Set time limit of extend/ retract movement
        self.linear_actuator.set_time_limit(30.0)
        
        # Start linear actuator Thread
        self.linear_actuator.start()

import threading
    
if __name__ == "__main__":
    config = umethods.load_config('../../../conf/config.properties')

    ll = LiftLevellingModule(config)
    # ll.pack_id = ll.create_data_pack(task_id=0)

    threading.Thread(target=ll.thread_get_status).start()  
    
    ll.start()

    
    
    
    # # Create data pack
    # ll.laser_distance.set_pack_id(ll.laser_distance.create_data_pack(task_id=1)) 
    # print(f"pack created, pack_id = {ll.laser_distance.pack_id}")
    
    # # Set moving direction
    # ll.laser_distance.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
    # print(f"direction indicator set, move_dir = {ll.laser_distance.move_dir}")
    
    # # Start laser distance Thread
    # ll.laser_distance.start()
    
    # # Set time limit of extend/ retract movement
    # ll.linear_actuator.set_time_limit(20.0)
    
    # # Start linear actuator Thread
    # ll.linear_actuator.start()
    