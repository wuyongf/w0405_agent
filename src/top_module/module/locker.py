import serial
import time
from datetime import datetime
import src.utils.methods as umethods
import src.top_module.port as port
# Voltage = 12V


class Locker():
    def __init__(self, port_config):
        self.sid = port_config.get('LOCK', 'sid')
        self.port = port.port().port_match(self.sid)
        print(self.port)
        self.baudrate = 9600
        self.ser = serial.Serial(self.port, self.baudrate)
        self.time_interval = 0.3
        print("SerialController initialized")
        self.open_all = [0x8A, 0x01, 0x00, 0x11, 0x9A]  # open all
        self.open_portA = [0x8A, 0x01, 0x01, 0x11, 0x9B]  # open port A
        self.read_all = [0x80, 0x01, 0x00, 0x33, 0xB2]  # read all port
        self.read_portA = [0x80, 0x01, 0x01, 0x33, 0xB3]  # read port A

    def unlock(self):
        if self.ser and self.ser.is_open:
            try:
                send_data = serial.to_bytes(self.open_portA)
                self.ser.write(send_data)
                time.sleep(self.time_interval)
                len_return_data = self.ser.inWaiting()
            except serial.SerialException:
                print("[locker.py] failed to send unlock command")
        else:
            print("[locker.py] serial port is not open")

    def read_status(self):
        if self.ser and self.ser.is_open:
            while True:
                try:
                    send_data = serial.to_bytes(self.read_portA)
                    self.ser.write(send_data)
                    time.sleep(self.time_interval)
                    len_return_data = self.ser.inWaiting()

                    if len_return_data:
                        return_data = self.ser.read(len_return_data)
                        return_data_arr = list(bytearray(return_data))
                        print(return_data_arr)
                        for counter, data in enumerate(return_data_arr):
                            if counter == 3:
                                if data == 17:
                                    print('[locker.py] Get status: Locked')
                                    return True
                                if data == 0:
                                    print('[locker.py] Get status: Unlocked')
                                    return False
                        return False
                    else:
                        print('no data return')

                except serial.SerialException:
                    print("failed to send read command")
        else:
            print("serial port is not open")

    def is_closed(self):
        return self.read_status()

    
if __name__ == '__main__':
    # example usage
    port_config = umethods.load_config('../../../conf/port_config.properties')
    lock = Locker(port_config)
    # print(lock.sid)
    # lock.read_status()
    print(lock.is_closed())
    time.sleep(1)
    lock.unlock()
    time.sleep(1)
    print(lock.is_closed())
    # lock.read_status()
    
    # lock.read_status()  # return 'locked'/'unlocked'
