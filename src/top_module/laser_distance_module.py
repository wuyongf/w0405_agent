import serial
import time
from datetime import datetime


class laser():

    def __init__(self):
        self.port_left = '/dev/ttyUSB1'
        self.port_right = '/dev/ttyUSB2'
        self.baudrate = 115200
        self.left = serial.Serial(self.port_left, self.baudrate)
        self.right = serial.Serial(self.port_right, self.baudrate)
        self.time_interval = 0.015
        print("SerialController initialized")
        self.read_distant = [0x01, 0x03, 0x00, 0x24, 0x00, 0x02, 0x84, 0x00]  # all open
        self.laser_distance = []

    def collect_data(self, current_ser):
        if current_ser and current_ser.is_open:
            while True:
                try:
                    send_data = serial.to_bytes(self.read_distant)
                    current_ser.write(send_data)
                    time.sleep(self.time_interval)
                    len_return_data = current_ser.inWaiting()

                    if len_return_data:
                        return_data = current_ser.read(len_return_data)
                        return_data_arr = list(bytearray(return_data))
                        distant_data = return_data_arr[5] * 256 + return_data_arr[6]
                        print(distant_data)
                        if distant_data <= 100:
                            return distant_data

                except serial.SerialException:
                    print("failed to send unlock command")
        else:
            print("serial port is not open")

    def data_integration(self):
        self.laser_distance = []
        self.laser_distance.append(collect_data(self.left))
        self.laser_distance.append(collect_data(self.right))
        return laser_distance[0], self.laser_distance[1]


if __name__ == '__main__':
    laser = laser()
    laser.data_integration()