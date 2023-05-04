import time
import src.top_module.io_module.io_controller as ioController
import threading
import src.top_module.enums.enums_linear_actuator as LAEnum


# TBC: sleep listener

class LinearActuator():
    def __init__(self, COM):
        self.io = ioController.ioController(COM)
        self.time_limit = 2.0
        self.stop_flag = 0
        self.status = 1
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.extend_retract)

    # def wait(self, t, condition):
    #     for i in range(t * 10):
    #         print(i)
    #         if condition():
    #             return True
    #         time.sleep(0.1)
    #     return True

    # Extension Motion
    # def motion_extend(self):
    #     i = 0
    #     # y0 on
    #     self.io.y_control(self.io.y0_on)
    #     print('start extent')
    #     # start a thread to monitor x0 and time limit
    #     while self.stop_flag == 0:
    #         if self.stop_event.is_set():
    #             continue
    #         time.sleep(0.1)
    #         i += 1
    #         # if x0 = High,
    #         if self.io.x_get(0) == 1:
    #             self.io.y_control(self.io.y0_off)
    #             break
    #         # if time > time limit,
    #         elif i > (self.time_limit * 10):
    #             self.io.y_control(self.io.y0_off)
    #             print("Time out!")
    #             # TODO : Send error code to DB
    #             break
    #         elif self.stop_flag == 1:
    #             print("Force Stop!")
    #             # TODO : Send error code to DB
    #             break
    #     print('extend completed')

    def motion(self, type_name, on_control, off_control, x_address, status):
        if self.stop_event.is_set() or self.stop_flag == 1:
            print(f'{type_name}: Stop by Force stop')
            self.status = LAEnum.LinearActuatorStatus.Error
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
                self.status = LAEnum.LinearActuatorStatus.Error
                self.io.y_control(off_control)
                self.stop()
                # TODO: Send error code to database
                break

            # If stop flag is set, turn off Y1, print error message and break out of the loop
            elif self.stop_flag == 1:
                print(f'Error: {type_name} stopped')
                self.status = LAEnum.LinearActuatorStatus.Error
                self.io.y_control(off_control)
                self.stop()
                self.status = 0
                # TODO: Send error code to database
                break

    def motion_extend(self):
        self.motion("Extend", self.io.y0_on, self.io.y0_off,
                    0, LAEnum.LinearActuatorStatus.Extend)

    def motion_retract(self):
        self.motion("Retract", self.io.y1_on, self.io.y1_off,
                    1, LAEnum.LinearActuatorStatus.Retract)

    def stopAll(self):
        self.stop_flag = 1
        self.io.y_control(self.io.y0_off)
        self.io.y_control(self.io.y1_off)
        time.sleep(0.5)
        self.stop_flag = 0

    def extend_retract(self):
        self.status = 1
        self.stop_flag = 0
        while not self.stop_event.is_set():
            self.motion_extend()
            time.sleep(2)
            self.motion_retract()
            print('extend_retract_finished')
            break

    def set_timelimite(self, t):
        self.time_limit = t/2

    def start(self):
        self.run_thread.start()

    def stop(self):
        self.stop_event.set()
        self.stopAll()

    def get_status(self):
        return (self.status)

        pass


if __name__ == '__main__':
    la = LinearActuator('COM4')
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
