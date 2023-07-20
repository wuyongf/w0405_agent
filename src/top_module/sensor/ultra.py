import serial
import time
import threading
import src.utils.methods as umethods
import src.top_module.port as port
# Voltage = 9 - 36V

# Todo:
#   1. sql method
#   2. change probe 1 to 4 to front l,r & back l,r


class ultra:

    def __init__(self, prot_config) -> None:
        # self.sid = prot_config.get('ULTRA', 'sid')
        self.sid = "MI7XNGVG"
        self.port = port.port().port_match(self.sid)
        self.baudrate = 9600
        self.ser = serial.Serial(self.port, self.baudrate)
        self.time_interval = 0.235  # shd be fixed to 0.24
        print("SerialController initialized")
        self.command = [0x55, 0xAA, 0x01, 0x01, 0x01]
        self.ser = serial.Serial(self.port, self.baudrate)
        if self.ser.is_open:
            print("port open success")
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.collect_data,)
        
        self.init_distance = []
        self.prev_result = []
        self.counter = 0
        self.check_stability_flag = False
        self.threshold_percent = 0.05
        
        self.result = []
        self.data_list_FL = []
        self.data_list_FR = []
        self.check_flag = False
        self.door_is_opened = False
        
        self.check_door_counter = 0
        self.check_door_type = None
         
    def start(self): # Start Looping
        self.run_thread.start()
        
    def stop(self) :
        self.stop_event.set()     
        
    def store_data(self, data):
        self.data_list_FL.append(data[0])
        if len(self.data_list_FL) > 10:
            self.data_list_FL.pop(0)
        # print(self.data_list_FL)
        self.data_list_FR.append(data[1])
        if len(self.data_list_FR) > 10:
            self.data_list_FR.pop(0)
        # print(self.data_list_FR)


    def set_init_distance(self):
        # TODO: algorithm to define init distance
        self.init_distance = [self.result[0], self.result[1]]

    def data_handling(self, datahex):
        FL = (datahex[2]) * 256 + (datahex[3])
        BL = (datahex[4]) * 256 + (datahex[5])
        FR = (datahex[6]) * 256 + (datahex[7])
        BR = (datahex[8]) * 256 + (datahex[9])
        return [FL, FR, BL, BR]

    def collect_data(self):
        if self.ser and self.ser.is_open:
            while not self.stop_event.is_set():
                try:
                    send_data = serial.to_bytes(self.command)
                    self.ser.write(send_data)
                    time.sleep(self.time_interval)
                    len_return_data = self.ser.inWaiting()
                    if len_return_data == 13:
                        return_data = self.ser.read(len_return_data)
                        return_data_arr = bytearray(return_data)
                        appendStart = False  # flag for data matching
                        datahex = []  # empty arrays for temporally data transition
                        for data in return_data_arr:
                            if appendStart == True:  # Step 2: if header is found, data can be matched
                                datahex.append(data)
                            if data == 170:  # Step 1: 170 is the value of header, for data matching
                                appendStart = True
                        result = self.data_handling(datahex)
                        self.result = result
                        print(f"[ultra.py] {self.result}")
                        
                        if self.check_stability_flag == True:
                            self.check_float_stability()
                        
                        if self.check_flag == True:
                            self.check_distance()

                    else:
                        print("No data received")
                except Exception as e:
                    print("Exception occurred:", e)
                    pass

    def check_float_stability(self):
        if self.result[0] != 0 and self.result[1] != 0:
            if self.prev_result == []:
                self.prev_result = self.result
            print(f'[ultra.py] Check stability: no.{self.counter + 1}')
                
            for side in [0,1]:
                print(f'[ultra.py] prev_result: {self.prev_result[side]}')
                if abs((self.result[side] - self.prev_result[side]) / self.prev_result[side]) > self.threshold_percent:
                    self.prev_result[side] = self.result[side]
                    self.counter = 0
            
            self.counter += 1
            # print(self.counter)
            
            if self.counter >= 6:
                print("[ultra.py] Reading stable")
                self.counter = 0
                self.check_stability_flag = False
                self.set_init_distance()
                
    def find_init_distance(self):
        self.init_distance = []
        self.check_stability_flag = True # Start check stability
        while self.init_distance == []:
            time.sleep(0.2)
        print(f"[ultra.py] Set init distance : {self.init_distance}")
        return self.init_distance
    
    def start_check_distance(self):
        # if self.find_init_distance() is True:
        time.sleep(0.5)
        self.check_flag = True
        
    def check_distance(self):
        # algorithm to check door status using ultra sensor
        # will compare current distance with init distance
        try:           
            # case: if distance far away
            if self.result[0] - self.init_distance[0] > 100 or self.result[1] - self.init_distance[1] > 100:
                print("[ultra.py] checking door: far")
                # if prevous type is not far, reset counter
                if self.check_door_type != 'far':
                    # reset counter
                    self.check_door_type = 'far'
                    self.check_door_counter = 0
                else:
                    self.check_door_counter += 1
                            
            elif self.result[0] - self.init_distance[0] < -100 or self.result[1] - self.init_distance[1] < -100:
                print("[ultra.py] checking door: close")
                # if prevous type is not close, reset counter
                if self.check_door_type != 'close':
                    # reset counter
                    self.check_door_type = 'close'
                    self.check_door_counter = 0
                else:
                    self.check_door_counter += 1
                
            else:
                # reset counter
                self.check_door_type = None
                self.check_door_counter = 0
            
            # if counter >= 4, set door status is open
            if self.check_door_counter >= 3:
                self.door_is_opened = True
                
        except:
            pass
        
    # def check_distance(self):
    #     # TODO: algorithm to define distance
    #     try:
    #         counter = 0
    #         if (self.result[0] - self.init_distance[0] > 100 or self.result[1] - self.init_distance[1] > 100 or 
    #             self.result[0] - self.init_distance[0] < -100 or self.result[1] - self.init_distance[1] < -100):
    #             pass
            
    #         if self.result[0] - self.init_distance[0] > 100:
    #             print("FL is too far away")
    #             self.door_is_opened = True
    #         if self.result[1] - self.init_distance[1] > 100:
    #             print("FR is too far away")
    #             self.door_is_opened = True
    #         if self.result[0] - self.init_distance[0] < -100:
    #             print("FL is too close")
    #             self.door_is_opened = True
    #         if self.result[1] - self.init_distance[1] < -100:
    #             print("FR is too close")
    #             self.door_is_opened = True
    #     except:
    #         pass

    def stop_check_distance(self):
        self.check_flag = False
        # clean init distance & door status
        self.init_distance = []
        self.door_is_opened = False
        
    def get_door_status(self):
        return self.door_is_opened


    def close(self):
        self.ser.close()


if __name__ == '__main__':
    # Example usage:
    prot_config = umethods.load_config('../../../conf/port_config.properties')
    ultra = ultra(prot_config)
    # ultra.set_orgin_distance()
    # ultra.collect_data()
    ultra.start()
    time.sleep(0.5)
    ultra.find_init_distance()
    # ultra.start_check_distance()
    
    