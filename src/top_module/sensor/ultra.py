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

    def __init__(self, prot_config):
        self.sid = prot_config.get('ULTRA', 'sid')
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
        self.result = []
        self.data_list_FL = []
        self.data_list_FR = []
        self.check_flag = False
         
    def start(self):
        self.run_thread.start()
        
    def stop(self) :
        self.stop_event.set()       
        
    def start_check_distance(self):
        self.set_init_distance()
        time.sleep(0.5)
        self.check_flag = True
        
    def stop_check_distance(self):
        self.check_flag = False
        # clean init distance
        self.init_distance = []
        
    def store_data(self, data):
        self.data_list_FL.append(data[0])
        if len(self.data_list_FL) > 10:
            self.data_list_FL.pop(0)
        # print(self.data_list_FL)
        self.data_list_FR.append(data[1])
        if len(self.data_list_FR) > 10:
            self.data_list_FR.pop(0)
        # print(self.data_list_FR)


    def check_distance(self):
        # TODO: algorithm to define distance 
        if self.result[0] - self.init_distance[0] > 100:
            print("FL is too far away")
        if self.result[1] - self.init_distance[1] > 100:
            print("FR is too far away")


    def set_init_distance(self):
        # TODO: algorithm to define init distance
        self.init_distance = [self.result[0], self.result[1]]
        print(f"init_distance = {self.init_distance}")

    def data_handling(self, datahex):
        FL = (datahex[2]) * 256 + (datahex[3])
        BL = (datahex[4]) * 256 + (datahex[5])
        FR = (datahex[6]) * 256 + (datahex[7])
        BR = (datahex[8]) * 256 + (datahex[9])
        return [FL, FR, BL, BR]

    def collect_data(self):
        if self.ser and self.ser.is_open:
            while True:
                try:
                    send_data = serial.to_bytes(self.command)
                    self.ser.write(send_data)
                    time.sleep(self.time_interval)
                    len_return_data = self.ser.inWaiting()
                    # print(len_return_data)
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
                        # print(self.data_handling(datahex))  # return the
                        # self.store_data(result)
                        self.result = result
                        print(self.result)
                        if self.check_flag == True:
                            self.check_distance()
                            # print(self.result[0])

                    else:
                        print("No data received")
                except Exception as e:
                    print("Exception occurred:", e)
                    pass

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
    # ultra.set_init_distance()
    # time.sleep(0.5)
    ultra.start_check_distance()
    
    