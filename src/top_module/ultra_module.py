import serial
import time
# Voltage = 9 - 36V

# Todo:
#   1. sql method
#   2. change probe 1 to 4 to front l,r & back l,r

class ultra:
    def __init__(self):
        self.port = '/dev/ttyUSB2'
        self.baudrate = 9600
        self.ser = serial.Serial(self.port, self.baudrate)
        self.time_interval = 0.25                              # shd be fixed to 0.25
        print("SerialController initialized")
        self.command = [0x55, 0xAA, 0x01, 0x01, 0x01]
        
        self.ser = serial.Serial(port, baudrate)
        if self.ser.is_open:
            print("port open success")

    def data_handling(self, datahex):
        probe1 = (datahex[2]) * 256 + (datahex[3])
        probe2 = (datahex[4]) * 256 + (datahex[5])
        probe3 = (datahex[6]) * 256 + (datahex[7])
        probe4 = (datahex[8]) * 256 + (datahex[9])
        return probe1, probe2, probe3, probe4

    def collect_data(self):
        if self.ser and self.ser.is_open:
            while True:
                try:
                    send_data = serial.to_bytes(self.command)
                    self.ser.write(send_data)
                    time.sleep(time_interval)
                    len_return_data = self.ser.inWaiting()

                    if len_return_data:
                        return_data = self.ser.read(len_return_data)
                        return_data_arr = bytearray(return_data)
                        appendStart = False                             # flag for data matching
                        datahex = []                                    # empty arrays for temporally data transition
                        for data in return_data_arr:
                            if appendStart == True:                     # Step 2: if header is found, data can be matched
                                datahex.append(data)
                            if data == 170:                             # Step 1: 170 is the value of header, for data matching
                                appendStart = True
                        print(self.data_handling(datahex))              # return the value of probe 1 - 4
                    else:
                        print("No data received")
                except Exception as e:
                    print("Exception occurred:", e)
                    pass

    def close(self):
        self.ser.close()


if __name__ == '__main__':
    # Example usage:
    ultra = ultra()
    ultra.collect_data()