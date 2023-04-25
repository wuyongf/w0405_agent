import time
import src.top_module.io_module.io_controller_backup as io_controller

# TBC: sleep listener

class access_control():
    def __init__(self):
        self.io = io_controller.ioController()
        self.duration = 0.4
        self.time_limit = 2.0
        self.stop_flag = 0

    def flip(self):
        self.io.y_control(self.io.y2_on)     # y2 on
        self.io.y_control(self.io.y2_off)    # y2 off
        # wait for finish
        time.sleep(self.duration)
        # 90 degree
        self.io.y_control(self.io.y3_on)     # y3 on
        self.io.y_control(self.io.y3_off)    # y3 off


if __name__ == '__main__':
    ac = access_control()
    ac.flip()