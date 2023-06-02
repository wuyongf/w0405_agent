import threading
import time
import src.top_module.io_module.servo_motor as ServoMotor
import src.top_module.sensor.ultra as UltraSound
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
# import src.top_module.enums.enums_door_status as DoorEnum



class AccessControl():
    def __init__(self, config, port_config):
        self.nwdb = NWDB.TopModuleDBHandler(config, port_config)
        self.servo_motor = ServoMotor.ServoMotor(port_config)
        self.ultra = UltraSound.ultra(port_config)
        self.status_door = 0
        
    def get_status(self):
        pass
    
    def get_ultra_distance(self):
        # self.
        pass
    
    def get_door_status(self):
        pass
    
    def open_door(self):
        self.ultra.start()
        time.sleep(1)
        self.ultra.start_check_distance()
        self.servo_motor.servo_flip(0.4)
        
        
        # for loop (5) times:
        #   set init distance()    
        #   for loop (4) times:
        #       filp the phone()
        #   reset the init distance() if still fail
        # mission fail() if still cant open
        
        
    
if __name__ == "__main__":
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')

    ac = AccessControl(config, port_config)
    ac.open_door()