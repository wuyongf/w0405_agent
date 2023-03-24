import serial
import time
# Voltage = 9 - 36V


class ProbeReader:
    def __init__(self, port="/dev/ttyUSB2", baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
        if self.ser.is_open:
            print("port open success")

    def data_handling(self, datahex):
        probe1 = (datahex[2]) * 256 + (datahex[3])
        probe2 = (datahex[4]) * 256 + (datahex[5])
        probe3 = (datahex[6]) * 256 + (datahex[7])
        probe4 = (datahex[8]) * 256 + (datahex[9])
        return probe1, probe2, probe3, probe4

    def read_probes(self):
        while True:
            try:
                send_data = serial.to_bytes([0x55, 0xAA, 0x01, 0x01, 0x01])
                self.ser.write(send_data)
                time.sleep(0.25)
                len_return_data = self.ser.inWaiting()
                if len_return_data:
                    return_data = self.ser.read(len_return_data)
                    return_data_arr = bytearray(return_data)
                    # print(return_data_arr)
                    appendStart = False
                    datahex = []
                    for data in return_data_arr:
                        if appendStart == True:
                            datahex.append(data)
                        if data == 170:
                            appendStart = True
                    print(self.data_handling(datahex))
                else:
                    print("No data received")
            except Exception as e:
                print("Exception occurred:", e)
                pass

    def close(self):
        self.ser.close()


if __name__ == '__main__':
    # Example usage:
    reader = ProbeReader()
    probes = reader.read_probes()