import serial
import time
from datetime import datetime
# import src.utils.methods as umethods
# import src.top_module.port as port

# TBC: sleep listener


class ioController():

    def __init__(self, COM):
        self.port = COM
        self.baudrate = '38400'
        self.ser = serial.Serial(self.port, self.baudrate)
        self.time_interval = 0.1
        print("SerialController initialized")

        self.read = [0x01, 0x04, 0x00, 0x00, 0x00, 0x01, 0x31, 0xCA]  # get y1 status (Relay Status)
        self.y0_on = [0x01, 0x06, 0x00, 0x00, 0x00, 0x01, 0x48, 0x0A]  # linear actuator front
        self.y0_off = [0x01, 0x06, 0x00, 0x00, 0x00, 0x00, 0x89, 0xCA]
        self.y1_on = [0x01, 0x06, 0x00, 0x01, 0x00, 0x01, 0x19, 0xCA]  # linear actuator back
        self.y1_off = [0x01, 0x06, 0x00, 0x01, 0x00, 0x00, 0xD8, 0x0A]
        self.y2_on = [0x01, 0x06, 0x00, 0x02, 0x00, 0x01, 0xE9, 0xCA]  # phone servo = 0
        self.y2_off = [0x01, 0x06, 0x00, 0x02, 0x00, 0x00, 0x28, 0x0A]
        self.y3_on = [0x01, 0x06, 0x00, 0x03, 0x00, 0x01, 0xB8, 0x0A]  # phone servo = 90
        self.y3_off = [0x01, 0x06, 0x00, 0x03, 0x00, 0x00, 0x79, 0xCA]
        self.y4_on = [0x01, 0x06, 0x00, 0x04, 0x00, 0x01, 0x09, 0xCB]  # surface pro linear actuator power
        self.y4_off = [0x01, 0x06, 0x00, 0x04, 0x00, 0x00, 0xC8, 0x0B]  # cut the power
        self.y5_on = [0x01, 0x06, 0x00, 0x05, 0x00, 0x01, 0x58, 0x0B]  # push
        self.y5_off = [0x01, 0x06, 0x00, 0x05, 0x00, 0x00, 0x99, 0xCB]  # pull
        self.y6_on = [0x01, 0x06, 0x00, 0x06, 0x00, 0x01, 0xA8, 0x0B]  # iaq fan on
        self.y6_off = [0x01, 0x06, 0x00, 0x06, 0x00, 0x00, 0x69, 0xCB]  # iaq fan off
        self.y7_on = [0x01, 0x06, 0x00, 0x07, 0x00, 0x01, 0xF9, 0xCB]  # ventilation fan on
        self.y7_off = [0x01, 0x06, 0x00, 0x07, 0x00, 0x00, 0x38, 0x0B]  # ventilation fan off
        self.get_input = [0x01, 0x02, 0x00, 0x00, 0x00, 0x08, 0x79, 0xCC]  # read X0 - X7

    # def open_com(self):
    #     self.port = "COM3"
    #     self.baudrate = '38400'
    #     self.ser = serial.Serial(self.port, self.baudrate)

    def y_control(self, bytearray):
        send_data = serial.to_bytes(bytearray)
        self.ser.write(send_data)
        time.sleep(self.time_interval)

    def y_init(self, ):
        self.y_control(self.y0_off)
        self.y_control(self.y1_off)
        self.y_control(self.y2_off)
        self.y_control(self.y3_off)
        self.y_control(self.y4_off)
        self.y_control(self.y5_off)
        self.y_control(self.y6_off)
        self.y_control(self.y7_off)

    def get_inputStatus(self, x):
        send_data = serial.to_bytes(self.get_input)
        self.ser.write(send_data)
        time.sleep(self.time_interval)
        len_return_data = self.ser.inWaiting()
        if len_return_data:
            return_data = self.ser.read(len_return_data)
            return_data_arr = bytearray(return_data)
            print(return_data_arr)
            status = return_data_arr[3]
            status = format(int(status), '08b')
            ioport = 7 - int(x)
        return int(status[ioport])

    def x_get(self, x):
        return int(self.get_inputStatus(x))

    def linear_actuator(self, action):
        # Extension Motion
        if action == 1:
            self.y_control(self.y0_on)  # y0 on
            while True:  # start a thread to monitor x0
                if self.x_get(0) == 1:  # if x0 = High,
                    self.y_control(self.y0_off)
                    break
        # Retraction Motion
        if action == 0:
            self.y_control(self.y1_on)
            while True:  # start monitoring x0
                if self.x_get(1) == 1:
                    self.y_control(self.y1_off)  # if x0 = High,
                    break

    def phone_servo(self, duration):
        # 0 degree
        self.y_control(self.y2_on)  # y2 on
        self.y_control(self.y2_off)  # y2 off
        # wait for finish
        time.sleep(duration)
        # 90 degree
        self.y_control(self.y3_on)  # y3 on
        self.y_control(self.y3_off)  # y3 off

    def surfacepro_angle(self, angle):
        duration = 3
        # power on
        send_data = serial.to_bytes(self.y4_on)  # y4 on - power supply
        self.ser.write(send_data)
        time.sleep(self.time_interval)
        # up / down motion
        if angle == 'up':
            send_data = serial.to_bytes(self.y5_on)  # y5 on - up
            self.ser.write(send_data)
            time.sleep(self.time_interval)
        if angle == 'down':
            send_data = serial.to_bytes(self.y5_off)  # y5 off - down
            self.ser.write(send_data)
            time.sleep(self.time_interval)
        # wait for motion finish
        time.sleep(duration)
        # power off
        send_data = serial.to_bytes(self.y4_off)  # y4 on - power off
        self.ser.write(send_data)
        time.sleep(self.time_interval)

    def fan(self, fan, switch):
        if fan == 'iaq':
            if switch == 'on':
                send_data = serial.to_bytes(self.y6_on)  # y6 on - power supply
                self.ser.write(send_data)
                time.sleep(self.time_interval)
            if switch == 'off':
                send_data = serial.to_bytes(self.y6_off)  # y6 off - power off
                self.ser.write(send_data)
                time.sleep(self.time_interval)
        if fan == 'ventilation':
            if switch == 'on':
                send_data = serial.to_bytes(self.y7_on)  # y7 on - power supply
                self.ser.write(send_data)
                time.sleep(self.time_interval)
            if switch == 'off':
                send_data = serial.to_bytes(self.y7_off)  # y7 off - power off
                self.ser.write(send_data)
                time.sleep(self.time_interval)


if __name__ == '__main__':
    # example usage
    io = ioController("COM4")
    # io.y_control(io.y1_on)
    # io.y_control(io.y2_on)
    # io.phone_servo(0.5)
    io.y_init()

    # io.y_control(io.y7_on)
    # io.linear_actuator(1)           # Extension = 1
    # io.linear_actuator(0)           # Retraction = 0
    # io.phone_servo(0.3)             # 0.3s = duration time from 0 to 90 (half cycle of full motion)
    # io.surfacepro_angle('up')       # up / down in string
    # io.surfacepro_angle('down')     # up / down in string
    # io.fan('iaq','on')              # iaq fan on
    # io.fan('iaq','off')             # iaq fan off
    # io.fan('ventilation','on')      # ventilation fan on
    # io.fan('ventilation','off')     # ventilation fan off
    # io.get_inputStatus(0)           # Status of X0 - X7, High = 1 / Low = 0
