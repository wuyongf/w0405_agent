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

    def get_status(self, fan):
        if fan == 'iaq':
            return self.io.y_get(self.io.y6_get)
        elif fan == 'cooling':
            return self.io.y_get(self.io.y7_get)
        elif fan == 'all':
            return [self.io.y_get(self.io.y6_get),self.io.y_get(self.io.y7_get)]

    def test(self, fan):
        if fan == 'iaq':
            print(self.io.y_get(self.io.y6_get))
            print(self.io.y_get(self.io.y7_get))
        if fan == 'cooling':
            # print(f'iaq:{self.io.y_get(self.io.y6_get)}')
            print(f'cooling:{self.io.y_get(self.io.y7_get)}')

if __name__ == '__main__':
    port_config = umethods.load_config('../../../conf/port_config.properties')
    fan = fans(port_config)
    # fan.all_fan('on')
    # fan.all_fan('off')
    # fan.cooling_fan('on')
    # print(fan.get_status('all'))
    # time.sleep(2)
    # fan.test('cooling')
    # time.sleep(2)
    fan.test('cooling')