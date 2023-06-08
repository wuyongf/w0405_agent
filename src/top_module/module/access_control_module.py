import threading
import time
import src.top_module.io_module.servo_motor as ServoMotor
import src.top_module.sensor.ultra as UltraSound
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import src.top_module.enums.enums_module_status as MoEnum
# import src.top_module.enums.enums_door_status as DoorEnum

# TODO: Potential issue: Robot cant find the init distance if the door already opened at first
#                        Robot stuck at door position if the result remain 0 and the door keeps open

class AccessControl():
    def __init__(self, config, port_config):
        self.nwdb = NWDB.TopModuleDBHandler(config)
        self.servo_motor = ServoMotor.ServoMotor(port_config)
        self.ultra = UltraSound.ultra(port_config)
        self.servo_duration = 0.4
        self.door_status = MoEnum.AccessControlStatus.Closed
        self.init_distance = []
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.try_open_door,)
        
    def get_status(self):
        return self.door_status
    
    def check_door_status(self):
        while not self.stop_event.is_set():
            if self.ultra.get_door_status():
                self.set_status(MoEnum.AccessControlStatus.Opened)
                self.ultra.stop_check_distance()
                self.stop()
    
    def set_status(self, value):
        self.door_status = value
    
    # def get_door_status(self):
    #     return self.door_status
    
    def servo_flip(self):
        print("[access_control_module.py] Flip servo")
        self.servo_motor.servo_flip(duration = self.servo_duration)
    
    # def open_door(self):
    #     self.ultra.start()
    #     time.sleep(1)
    #     # self.ultra.start_check_distance()
    #     # self.servo_motor.servo_flip(0.4)
        
    def get_init_distance(self):
        # self.init_distance = self.ultra.find_init_distance()
        return self.ultra.find_init_distance()
    
    def start_check_distance(self):
        self.ultra.start_check_distance()
    
    def try_open_door(self):
        self.ultra.start()
        # self.start()
        time.sleep(1)
        
        for i in range(3):
            if i >=2:
                self.set_status(MoEnum.AccessControlStatus.Error)
                print('[access_control_module.py] Mission Fail!')
                self.ultra.stop_check_distance()
                self.ultra.stop()
                break
            # Get the initial distance
            if self.door_status == MoEnum.AccessControlStatus.Opened:
                self.ultra.stop()
                break
            self.get_init_distance()
            time.sleep(1)
            # Start checking distance (distance between robot and door)
            self.start_check_distance()
            time.sleep(1)
            
            for i in range(3):
                if i > 3 or self.door_status == MoEnum.AccessControlStatus.Opened:
                    break
                self.servo_flip()
                for t in range(5):
                    if t > 5:
                        break
                    time.sleep(1)
                    if self.ultra.get_door_status():
                        self.set_status(MoEnum.AccessControlStatus.Opened)
                        self.ultra.stop_check_distance()
                        print("DOOR OPENED")
                        break

        # for loop (5) times:
        #   set init distance()    
        #   for loop (4) times:
        #       filp the phone()
        #   reset the init distance() if still fail
        # mission fail() if still cant open

    def start(self): # Start Looping
        self.run_thread.start()
        
    def stop(self) :
        self.stop_event.set()  
        

if __name__ == "__main__":
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')

    ac = AccessControl(config, port_config)
    ac.start()
    time.sleep(5)
    print(ac.get_status())
    # ac.get_door_status()
