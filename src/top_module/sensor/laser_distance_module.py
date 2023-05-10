import serial
import time
from datetime import datetime
import random 
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import threading
# import src.top_module.port as port
import src.top_module.enums.enums_laser_distance as LDEnum
import src.top_module.enums.enums_linear_actuator as LAEnum


class LaserDistanceSensor():

    def __init__(self):
        # self.sid_left = umethods.load_config('../../../conf/port_config.properties').get('LASER_L', 'sid')
        # self.sid_right = umethods.load_config('../../../conf/port_config.properties').get('LASER_R', 'sid')
        # self.port_left = port.port().port_match(self.sid_left)
        # self.port_right = port.port().port_match(self.sid_right)
        self.baudrate = 115200
        self.config = umethods.load_config('../../../conf/config.properties')
        self.nwdb = NWDB.robotDBHandler(self.config)
        # # self.left = serial.Serial(self.port_left, self.baudrate)
        # # self.right = serial.Serial(self.port_right, self.baudrate)
        self.time_interval = 0.015
        print("SerialController initialized")
        self.read_distant = [0x01, 0x03, 0x00, 0x24,
                             0x00, 0x02, 0x84, 0x00]  # all open
        self.laser_distance = []
        self.start_flag = 0
        self.retract_flag = False
        self.data_stack_left = []
        self.data_stack_right = []
        self.stop_event = threading.Event()
        
        self.pack_id = 11
        self.move_dir = 0
        self.run_thread = threading.Thread(target=self.store_data, args=(LDEnum.LaserDistanceSide.Left.value,))
        # self.run_thread_r = threading.Thread(target=self.store_data, args=(LDEnum.LaserDistanceSide.Right.value,))
        
        
    # def set_thread(self, pack_id, current_ser, move_dir):
    #     self.run_thread = threading.Thread(target=self.store_data, args=(pack_id, current_ser, move_dir))
    
    def set_retract_flag(self, event):
        self.retract_flag = event
    
    def set_move_dir(self, dir):
        self.move_dir = dir
    
    def set_pack_id(self, id):
        self.pack_id = id
    
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


    def insert_data(self, data, current_ser):
        list_to_str = ','.join([str(elem) for elem in data])
        data  = [] #clean data stack
        self.nwdb.InsertDistanceChunk(self.pack_id,list_to_str, list_to_str, self.move_dir)

    def create_data_pack(self, task_id):
        # TODO: task_id
        return self.nwdb.CreateDistanceDataPack(task_id)

    def store_data(self, current_ser):
        """
        Collects data and stores it in the database.
        """
        distance_data = []
        collecting_data = True
        while collecting_data:
            # collected_data = self.collect_data(current_ser)
            collected_data = round(self.debug_generate_random_number(), 5)
            distance_data.append(collected_data)
            # print(data_stack)
            
            if self.stop_event.is_set():
                print('finish, Upload immediately')
                self.insert_data(distance_data, current_ser)
                distance_data = [] #clean data stack
                self.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
                break
                               
            if self.retract_flag == True:                    # insert immediately
                print('interrupt, Upload immediately')
                self.insert_data(distance_data, current_ser)
                distance_data = [] #clean data stack
                
                time.sleep(1)
                self.set_move_dir(LAEnum.LinearActuatorStatus.Retract.value)
                print(f"direction indicator set, move_dir = {self.move_dir}")
                self.retract_flag = False
                     
            elif len(distance_data) > 200:
                # insert if data stack full
                print('insert to db')
                self.insert_data(distance_data, current_ser)
                distance_data = [] #clean data stack
                 # insert with linear actuator move_dir
            
    def start(self):
        self.run_thread.start()
        time.sleep(0.1)
        print("Start Thread")
        
    def stop(self):
        self.stop_event.set()
        print('Stop Thread')
        
if __name__ == '__main__':
    # laser = LaserDistanceSensor('COM5', 'COM7')
    # print(laser.data_integration())
    laser = LaserDistanceSensor()
    # laser.debug_generate_random_number()
    laser.retract_flag = False
    laser.set_pack_id(12)
    #******************** move_dir cannot be argument
    # laser.set_thread(1,1,laser.move_dir)
    laser.start()
    time.sleep(5)
    laser.set_move_dir(1)
    # laser.stop()
    
    # laser.retract_flag = True
    time.sleep(5)
    # laser.start()
    
    # laser.store_data(1,1,1)

