import time
import src.top_module.io_module.io_controller as io_controller


# TBC: sleep listener

class linear_actuator():
    def __init__(self):
        self.io = io_controller.ioController()
        self.time_limit = 2.0
        self.stop_flag = 0

    def wait(self, t, condition):
        for i in range(t * 10):
            print(i)
            if condition():
                return True
            time.sleep(0.1)
        return True

    # Extension Motion
    def extend(self, ):
        self.stop_flag = 0
        i = 0
        # y0 on
        self.io.y_control(self.io.y0_on)
        # start a thread to monitor x0 and time limit
        while True:
            time.sleep(0.1)
            i += 1
            # if x0 = High,
            if self.io.x_get(0) == 1:
                self.io.y_control(self.io.y0_off)
                break
            # if time > time limit,
            elif i > (self.time_limit * 10):
                self.io.y_control(self.io.y0_off)
                print("Time out!")
                # TODO : Send error code to DB
                break
            elif self.stop_flag == 1:
                print("Force Stop!")
                # TODO : Send error code to DB
                break

    def retract(self):
        self.stop_flag = 0
        i = 0
        # y1 on
        self.io.y_control(self.io.y1_on)
        # start a thread to monitor x1 and time limit
        while True:
            time.sleep(0.1)
            i += 1
            # if x1 = High,
            if self.io.x_get(1) == 1:
                self.io.y_control(self.io.y1_off)
                break
            # if time > time limit,
            elif i > (self.time_limit * 10):
                self.io.y_control(self.io.y1_off)
                print("Time out!")
                # TODO : Send error code to DB
                break
            elif self.stop_flag == 1:
                print("Force Stop!")
                # TODO : Send error code to DB
                break

    def stopAll(self):
        self.stop_flag = 1
        self.io.y_control(self.io.y0_off)
        self.io.y_control(self.io.y1_off)
        time.sleep(0.5)
        self.stop_flag = 0


if __name__ == '__main__':
    la = linear_actuator()
    la.extend()
