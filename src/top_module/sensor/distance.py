import serial
import time
from datetime import datetime
import random 
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import threading
import src.top_module.port as port
import src.top_module.enums.enums_laser_distance as LDEnum
import src.top_module.enums.enums_linear_actuator as LAEnum


class LaserDistanceSensor():

    def __init__(self, config, port_config):
        self.sid_left = port_config.get('LASER_L', 'sid')
        self.sid_right = port_config.get('LASER_R', 'sid')
        self.port_left = port.port().port_match(self.sid_left)
        self.port_right = port.port().port_match(self.sid_right)
        self.baudrate = 115200
        # self.config = umethods.load_config('../../../conf/config.properties')
        self.nwdb = NWDB.TopModuleDBHandler(config)
        self.left = serial.Serial(self.port_left, self.baudrate)
        self.right = serial.Serial(self.port_right, self.baudrate)
        self.time_interval = 0.015
        print("SerialController initialized")
        self.read_distant = [0x01, 0x03, 0x00, 0x24,
                             0x00, 0x02, 0x84, 0x00]  # all open
        self.laser_on = [0x01, 0x10, 0x00, 0x07, 0x00, 0x01, 0x02, 0x00, 0x01, 0x66, 0x27]
        self.laser_off = [0x01, 0x10, 0x00, 0x07, 0x00, 0x01, 0x02, 0x00, 0x00, 0xA7, 0xE7]
        self.laser_distance = []
        self.start_flag = 0
        self.retract_flag = False
        self.data_stack_left = []
        self.data_stack_right = []
        self.stop_event = threading.Event()
        
        self.pack_id = 50
        self.move_dir = 1
        self.run_thread = threading.Thread(target=self.store_data,)
        # self.run_thread_r = threading.Thread(target=self.store_data, args=(LDEnum.LaserDistanceSide.Right.value,))
        
        
    # def set_thread(self, pack_id, current_ser, move_dir):
    #     self.run_thread = threading.Thread(target=self.store_data, args=(pack_id, current_ser, move_dir))
    
    def laser_control(self, signal):
        if signal == 1:
            command = self.laser_on
        if signal == 0:
            command = self.laser_off
        if self.left.is_open:
            try:
                send_data = serial.to_bytes(command)
                self.left.write(send_data)
                print(f'laser_l: {signal}')
                time.sleep(self.time_interval)
            except serial.SerialException:
                    print("failed to send command")
        if self.right.is_open:
            try:
                send_data = serial.to_bytes(command)
                self.right.write(send_data)
                print(f'laser_r: {signal}')
                time.sleep(self.time_interval)
            except serial.SerialException:
                    print("failed to send command")

        

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
                        # print(return_data)
                        if len(return_data_arr) == 9:
                            
                            distant_data = return_data_arr[5] * \
                                256 + return_data_arr[6]
                            # print(return_data_arr)
                            # print(distant_data)
                            if distant_data <= 550:
                                return distant_data
                            elif distant_data >550:
                                return 700
                        elif len(return_data_arr) == 5:
                            return 0
                            # print(f'***Error {return_data}')

                except serial.SerialException:
                    print("failed to send command")
        else:
            print("serial port is not open")

    def debug_generate_random_number(self):
        while True:
            n = random.random()
            time.sleep(0.01)
            # print(n)
            return(n)
    
    def data_integration(self):
        while True:
            self.laser_distance = [0,0]
            self.laser_distance[0]=self.collect_data(self.left)
            self.laser_distance[1]=self.collect_data(self.right)
            # self.laser_distance[0]=self.debug_generate_random_number()
            # self.laser_distance[1]=self.debug_generate_random_number()
            # print(self.laser_distance)
            return self.laser_distance[0], self.laser_distance[1]


    def insert_data(self, data_l, data_r):
        list_to_str_l = ','.join([str(elem) for elem in data_l])
        list_to_str_r = ','.join([str(elem) for elem in data_r])
        data_l  = [] #clean data stack
        data_r  = [] #clean data stack
        self.nwdb.InsertDistanceChunk(self.pack_id, list_to_str_l, list_to_str_r, self.move_dir)

    def create_data_pack(self, task_id):
        # TODO: task_id
        return self.nwdb.CreateDistanceDataPack(task_id)

    def store_data(self):
        """
        Collects data and stores it in the database.
        """
        collected_data_l = []
        collected_data_r = []
        collecting_data = True
        while collecting_data:
            # collected_data = self.collect_data(current_ser)
            # collected_data = round(self.debug_generate_random_number(), 5)
            collected_data = self.data_integration()
            collected_data_l.append(collected_data[0])
            collected_data_r.append(collected_data[1])
            # print(data_stack)
            
            if self.stop_event.is_set():
                print('finish, Upload immediately')
                self.insert_data(collected_data_l, collected_data_r)
                collected_data_l = [] #clean data stack
                collected_data_r = [] #clean data stack
                self.set_move_dir(LAEnum.LinearActuatorStatus.Extend.value)
                break
                               
            if self.retract_flag == True:                    # insert immediately
                print('interrupt, Upload immediately')
                self.insert_data(collected_data_l, collected_data_r)
                collected_data_l = [] #clean data stack
                collected_data_r = [] #clean data stack
                time.sleep(1)
                self.set_move_dir(LAEnum.LinearActuatorStatus.Retract.value)
                print(f"direction indicator set, move_dir = {self.move_dir}")
                self.retract_flag = False
                     
            elif len(collected_data_l) > 200:
                # insert if data stack full
                print('insert to db')
                self.insert_data(collected_data_l, collected_data_r)
                collected_data_l = [] #clean data stack
                collected_data_r = [] #clean data stack
                 # insert with linear actuator move_dir
            
    def start(self):
        self.run_thread.start()
        time.sleep(0.1)
        print("Start Thread")
        
    def stop(self):
        self.stop_event.set()
        print('Stop Thread')
        
if __name__ == '__main__':
    # Example usage:
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')

    laser = LaserDistanceSensor(config, port_config)
    time.sleep(1)
    # laser.laser_control(1)       #signal = 1/0 , 1 = on, 0 = off
    # laser.store_data()
    
    # laser.collect_data(laser.left)

    # laser = LaserDistanceSensor('COM5', 'COM7')
    # print(laser.data_integration())
    # laser.debug_generate_random_number()
    # laser.retract_flag = False
    # laser.set_pack_id(12)
    # #******************** move_dir cannot be argument
    # # laser.set_thread(1,1,laser.move_dir)
    laser.start()
    time.sleep(50)
    # laser.run_thread.join()
    # laser.start()
    # laser.set_move_dir(1)
    laser.stop()
    
    # # laser.retract_flag = True
    # time.sleep(5)
    # laser.start()
    
    # laser.store_data(1,1,1)

