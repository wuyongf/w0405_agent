import time
import src.top_module.io_module.io_controller as ioController
import threading
import src.utils.methods as umethods
# import src.top_module.enums.enums_linear_actuator as LAEnum
from typing import Callable

class ServoMotor():
    def __init__(self, port_config):
        self.io = ioController.ioController(port_config)
        # self.time_limit = 2.0
        # self.stop_flag = 0
        # self.status = LAEnum.LinearActuatorStatus.Idle.value
        self.stop_event = threading.Event()
        # self.run_thread = threading.Thread(target=self.extend_retract, args=(callback_direction, callback_finish,))
        
    def servo_flip(self, duration):

        for i in range(3):
            # 0 degree
            self.io.y_control(self.io.y3_off)  # y2 on
            # self.io.y_control(self.io.y3_off)  # y2 off
            # wait for finish
            time.sleep(duration)
            # 90 degree
            self.io.y_control(self.io.y2_on)  # y3 on
            

            # self.io.y_control(self.io.y3_off)  # y2 off
        
if __name__ == '__main__':
    port_config = umethods.load_config('../../../conf/port_config.properties')
    servo = ServoMotor(port_config)
    servo.servo_flip(duration=0.5)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
    # time.sleep(2)
    # servo.servo_flip(duration=0.2)
