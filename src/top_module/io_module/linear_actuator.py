import time
import src.top_module.io_module.io_controller as ioController
import threading
import src.top_module.enums.enums_linear_actuator as LAEnum
from typing import Callable
# import src.utils.methods as umethods
# import src.top_module.port as port


# TBC: sleep listener

class LinearActuator():
    def __init__(self, COM: str, callback: Callable)->None:
        self.io = ioController.ioController(COM)
        self.time_limit = 2.0
        self.stop_flag = 0
        self.status = LAEnum.LinearActuatorStatus.Idle.value
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.extend_retract, args=(callback,))
    
    
    def setCOM(self, COM):
        self.io = ioController.ioController(COM)

    def motion(self, type_name, on_control, off_control, x_address, status):
        if self.stop_event.is_set() or self.stop_flag == 1:
            print(f'{type_name}: Stop by Force stop')
            self.status = LAEnum.LinearActuatorStatus.Error.value
            return
        i = 0
        # Turn on Y1 to start retracting
        self.io.y_control(on_control)
        self.status = status
        print(f'Starting {type_name}')

        # Start a thread to monitor X1 and time limit
        while True:
            time.sleep(0.1)
            i += 1

            # If X1 is high, retract is completed, turn off Y1 and break out of the loop
            if self.io.x_get(x_address) == 1:
                self.io.y_control(off_control)
                print(f'{type_name} completed')
                break

            # If time limit is reached, turn off Y1, print error message and break out of the loop
            elif i > (self.time_limit * 10):
                print(f'Error: {type_name} time limit reached')
                self.status = LAEnum.LinearActuatorStatus.Error.value
                self.io.y_control(off_control)
                self.stop()
                # TODO: Send error code to database
                break

            # If stop flag is set, turn off Y1, print error message and break out of the loop
            elif self.stop_flag == 1:
                print(f'Error: {type_name} stopped')
                self.status = LAEnum.LinearActuatorStatus.Error.value
                self.io.y_control(off_control)
                self.stop()
                self.status = 0
                # TODO: Send error code to database
                break

    def motion_extend(self):
        self.motion("Extend", self.io.y0_on, self.io.y0_off,
                    0, LAEnum.LinearActuatorStatus.Extend.value)

    def motion_retract(self):
        self.motion("Retract", self.io.y1_on, self.io.y1_off,
                    1, LAEnum.LinearActuatorStatus.Retract.value)

    def stopAll(self):
        self.stop_flag = 1
        self.io.y_control(self.io.y0_off)
        self.io.y_control(self.io.y1_off)
        time.sleep(0.5)
        self.stop_flag = 0

    def extend_retract(self, callback):
        self.status = 1
        self.stop_flag = 0
        while not self.stop_event.is_set():
            self.motion_extend()
            time.sleep(2)
            # if callable(callback):
                # callback()
            callback()
            time.sleep(2)
            self.motion_retract()
            print('extend_retract_finished')
            break

    def callback_test(self):
        print('callback: extend finish')

    # def thread_target(self,callback):
    #     self.extend_retract(callback)

    def set_timelimite(self, t):
        self.time_limit = t/2
        
    def get_status(self):
        return (self.status)
    
    def start(self):
        self.run_thread.start()

    def stop(self):
        self.stop_event.set()
        self.stopAll()

        pass


if __name__ == '__main__':
    def cb():
        print('cb')
        
    la = LinearActuator('COM6', cb)
    print(LAEnum.LinearActuatorStatus.Extend.value)
    la.set_timelimite(10.0)
    # la.extend()
    # time.sleep(2)
    # la.retract()
    la.start()
    # time.sleep(2)
    # la.stop()
    # la.extend_retract()
    print(la.status)
    time.sleep(2)
    print(la.status)
    time.sleep(2)
    print(la.status)
    time.sleep(2)
    print(la.status)
    time.sleep(2)
    print(la.status)
    time.sleep(2)
    print(la.status)
    time.sleep(2)
    print(la.status)
    time.sleep(2)
