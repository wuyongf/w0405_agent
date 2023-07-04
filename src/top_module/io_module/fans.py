import time
import src.top_module.io_module.io_controller as ioController
import threading
import src.utils.methods as umethods


class fans():
    def __init__(self, port_config):
        self.io = ioController.ioController(port_config)
        self.stop_event = threading.Event()

    def iaq_fan(self, set):
        if set == 'on':
            self.io.y_control(self.io.y6_off)
        if set == 'off':
            self.io.y_control(self.io.y6_on)

    def cooling_fan(self, set):
        if set == 'on':
            self.io.y_control(self.io.y7_off)
        if set == 'off':
            self.io.y_control(self.io.y7_on)

    def all_fan(self, set):
        if set == 'on':
            self.io.y_control(self.io.y6_off)
            self.io.y_control(self.io.y7_off)
        if set == 'off':
            self.io.y_control(self.io.y6_on)
            self.io.y_control(self.io.y7_on)


if __name__ == '__main__':
    port_config = umethods.load_config('../../../conf/port_config.properties')
    fan = fans(port_config)
    fan.all_fan(1)