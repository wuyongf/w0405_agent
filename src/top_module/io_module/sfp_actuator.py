import time
import src.top_module.io_module.io_controller as ioController
import threading
import src.utils.methods as umethods

class sfp_actuator():
    def __init__(self, port_config):
        self.io = ioController.ioController(port_config)
        self.stop_event = threading.Event()
        self.duration = 14

    def action(self, motion):
        if motion == 'down':
            print('down')
            self.io.y_control(self.io.y5_off)   # push
            self.io.y_control(self.io.y4_on)    # power on
            time.sleep(self.duration)           # wait for motion finish
            self.io.y_control(self.io.y4_off)   # power off
        if motion == 'up':
            print('up')
            self.io.y_control(self.io.y5_on)    # pull
            self.io.y_control(self.io.y4_on)    # power on
            time.sleep(self.duration)           # wait for motion finish
            self.io.y_control(self.io.y4_off)   # power off
        
if __name__ == '__main__':
    port_config = umethods.load_config('../../../conf/port_config.properties')
    actuator = sfp_actuator(port_config)
    actuator.action('up')
    actuator.action('down')