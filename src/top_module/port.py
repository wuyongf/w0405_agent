import pyudev
import serial


class port():

    def __init__(self):
        self.context = pyudev.Context()

    def port_match(self, sid):
        for device in self.context.list_devices(subsystem='tty'):
            serial_number = device.get('ID_SERIAL_SHORT')
            if sid == serial_number:
                serial_port = device.device_node
                return serial_port

    def list_ports(self):
        for device in self.context.list_devices(subsystem='tty'):
            vid = device.get('ID_VENDOR_ID')
            pid = device.get('ID_MODEL_ID')
            serial_number = device.get('ID_SERIAL_SHORT')
            serial_port = device.device_node
            print(vid, pid, serial_number, serial_port)