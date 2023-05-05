import serial
import time
from datetime import datetime
import random 

class LaserDistanceSensor():

    def __init__(self, COM_L, COM_R):
        self.port_left = 'COM5'
        self.port_right = 'COM7'
        self.baudrate = 115200
        # self.left = serial.Serial(self.port_left, self.baudrate)
        # self.right = serial.Serial(self.port_right, self.baudrate)
        self.time_interval = 0.015
        print("SerialController initialized")
        self.read_distant = [0x01, 0x03, 0x00, 0x24,
                             0x00, 0x02, 0x84, 0x00]  # all open
        self.laser_distance = []
        self.start_flag = 0
        self.data_stack_left = []
        self.data_stack_right = []
        

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
                        print(return_data)
                        if len(return_data_arr) == 9:
                            
                            distant_data = return_data_arr[5] * \
                                256 + return_data_arr[6]
                            # print(return_data_arr)
                                
                            if distant_data <= 500:
                                return distant_data
                        else :
                            # print(f'***Error {return_data}')
                            # return 0
                            pass

                except serial.SerialException:
                    print("failed to send unlock command")
        else:
            print("serial port is not open")

    def data_integration(self):
        while True:
            self.laser_distance = [0,0]
            self.laser_distance[0]=self.collect_data(self.left)
            self.laser_distance[1]=self.collect_data(self.right)
            print(self.laser_distance)
            # return self.laser_distance[0], self.laser_distance[1]

    def debug_generate_random_number(self):
        while True:
            n = random.random()
            time.sleep(0.015)
            # print(n)
            return(n)
    

    def store_data(self, current_ser):
        stop = 0
        while stop != 1:
            # collected_data = self.collect_data(current_ser)
            collected_data = round(self.debug_generate_random_number(), 5)
            self.data_stack_right.append(collected_data)
            print(self.data_stack_right)
            if len(self.data_stack_right) > 600:
                 stop = 1
                 listToStr = ','.join([str(elem) for elem in self.data_stack_right])
                 print(len(listToStr))
                 print(listToStr)
            
            

if __name__ == '__main__':
    # laser = LaserDistanceSensor('COM5', 'COM7')
    # print(laser.data_integration())
    laser = LaserDistanceSensor('COM1', 'COM1')
    # laser.debug_generate_random_number()
    laser.store_data("")
