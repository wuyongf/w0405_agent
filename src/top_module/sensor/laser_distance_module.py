import serial
import time
from datetime import datetime
import random 
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods

class LaserDistanceSensor():

    def __init__(self, COM_L, COM_R):
        self.port_left = 'COM1'
        self.port_right = 'COM1'
        self.baudrate = 115200
        self.config = umethods.load_config('../../../conf/config.properties')
        self.nwdb = NWDB.robotDBHandler(self.config)
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

    def debug_generate_random_number(self):
        while True:
            n = random.random()
            time.sleep(0.015)
            # print(n)
            return(n)
    
    def data_integration(self):
        while True:
            self.laser_distance = [0,0]
            # self.laser_distance[0]=self.collect_data(self.left)
            # self.laser_distance[1]=self.collect_data(self.right)
            self.laser_distance[0]=self.debug_generate_random_number()
            self.laser_distance[1]=self.debug_generate_random_number()
            print(self.laser_distance)
            # return self.laser_distance[0], self.laser_distance[1]

    def create_data_pack(self, task_id):
        # TODO: task_id
        return self.nwdb.CreateDistanceDataPack(task_id)

    def store_data(self, pack_id, current_ser, move_dir):
        data_stack = []
        stop = 0
        while stop != 1:
            # collected_data = self.collect_data(current_ser)
            collected_data = round(self.debug_generate_random_number(), 5)
            data_stack.append(collected_data)
            # print(data_stack)
            if len(data_stack) > 500:
                #  stop = 1
                 list_to_str = ','.join([str(elem) for elem in data_stack])
                 data_stack = [] #clean data stack
                #  print(len(list_to_str))
                #  print(list_to_str)
                 print('insert to db')
                 self.nwdb.InsertDistanceChunk(pack_id,list_to_str,current_ser,move_dir)
                 # insert with linear actuator move_dir
            
            

if __name__ == '__main__':
    # laser = LaserDistanceSensor('COM5', 'COM7')
    # print(laser.data_integration())
    laser = LaserDistanceSensor('COM1', 'COM1')
    # laser.debug_generate_random_number()
    # laser.store_data("")
