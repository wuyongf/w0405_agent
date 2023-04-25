import serial
import time
import sys
import logging
import os
import datetime
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import src.top_module.rules as rule

class IaqSensor():
    def __init__(self, config, COM, Ti):
        self.port = COM
        self.bandwidth = '9600'
        self.count = 0
        self.GG = 0
        self.time_interval = Ti
        self.command = [0x01, 0x03, 0x00, 0x00, 0x00, 0x0B, 0x04, 0x0D]
        self.task_mode = 0
        self.column_items = ["co2", "tvoc", "hcho", "pm25", "rh", "temperature", "pm10", "pm1", "lux", "mcu_temperature", "db"]
        self.nwdb = NWDB.robotDBHandler(config)
        self.rules = rule.user_rules("none", 300, "LOW")
        self.data_stack = []

    def get_data(self, datahex):
        co2 = (datahex[0] << 8 | datahex[1])
        tvoc = (datahex[2] << 8 | datahex[3])
        ch2o = (datahex[4] << 8 | datahex[5])
        pm25 = (datahex[6] << 8 | datahex[7])
        humi = (datahex[8] << 8 | datahex[9]) / 100
        temp = (datahex[10] << 8 | datahex[11]) / 100
        pm10 = (datahex[12] << 8 | datahex[13])
        pm01 = (datahex[14] << 8 | datahex[15])
        lux = (datahex[16] << 8 | datahex[17])
        mcu_temp = (datahex[18] << 8 | datahex[19]) / 100
        db = (datahex[20] << 8 | datahex[21])

        return [co2, tvoc, ch2o, pm25, humi, temp, pm10, pm01, lux, mcu_temp, db]

    def data_insert(self, value):
        print("dataInsert")
        self.nwdb.InsertIaqData("sensor.iaq.history", self.column_items, value)

    def data_stream(self, value):
        print("dataStream")
        self.nwdb.InsertIaqData("sensor.iaq.stream", self.column_items, value)


    def set_task_mode(self, e):
        self.task_mode = e
        print(self.task_mode)

    def run(self):
        self.collect_data()

    def data_store(self, dataset):
        self.data_stack.append(dataset)
        if len(self.data_stack) >= 5:
            self.check_stack(self.data_stack)
            # clear the stack
            self.data_stack.clear()

    def get_rules_column(self, dataset, column):
        return [i.get(column) for i in dataset]

    # NOTE:
    def check_stack(self, data_stack):
        # mySQL get (type, threshold, limit_type) as list
        rules_list = self.nwdb.GetUserRules()
        print(rules_list)
        rules_type_list = self.get_rules_column(rules_list, "data_type")
        rules_threshold_list = self.get_rules_column(rules_list, "threshold")
        rules_limit_type_list = self.get_rules_column(rules_list, "limit_type")

        for data in data_stack:
            for row_num, row_value in enumerate(rules_type_list):
                try:
                    # Compare with rules_type_list, find the index of data
                    col = self.column_items.index(row_value)
                    print("check : ", data, " Type : ", row_value, " | col : ", col, " Limit Type : ", rules_limit_type_list[row_num], " Threshold : ", rules_threshold_list[row_num], " Value : ", data[col])
                    if rules_limit_type_list[row_num] == "HIGH" and data[col] > rules_threshold_list[row_num]: # TODO: change to threshold in each row
                        print("*** Higher then threshold, Type : ", row_value," Threshold : ", rules_threshold_list[row_num], " Value : ", data[col])

                    elif rules_limit_type_list[row_num] == "LOW" and data[col] < rules_threshold_list[row_num]:
                        print("*** Lower then threshold, Type : ", row_value," Threshold : ", rules_threshold_list[row_num], " Value : ", data[col])

                except:
                    print("Except: No matched data type.", self.rules.type)




    def collect_data(self):
        ser = serial.Serial(self.port, self.bandwidth)  # Select Serial Port and bandwidth

        while True:
            try:
                named_tuple = time.localtime()  # get struct_time
                time_string = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)

                if ser.is_open:
                    # print("port open success")
                    send_data = serial.to_bytes(self.command)
                    ser.write(send_data)  # 发送命令
                    time.sleep(0.1)  # 延时，否则len_return_data将返回0，此处易忽视！！！
                    len_return_data = ser.inWaiting()  # 获取缓冲数据（接收数据）长度

                    if len_return_data:
                        return_data = ser.read(len_return_data)  # 读取缓冲数据
                        return_data_arr = bytearray(return_data)
                        count = 1
                        # print(return_data_arr)
                        rawdata = []

                        for data in return_data_arr:
                            if 4 <= count <= 25:
                                rawdata.append(data)
                            count += 1

                        result = self.get_data(rawdata)
                        print(result)

                        if sum(result) < 30000:

                            if self.task_mode:
                                # Insert to mySQL
                                self.data_store(result)
                                self.data_insert(result)
                                pass
                                # self.check_stack(result)


                            # Stream to mySQL
                            self.data_stream(result)
                            time.sleep(self.time_interval)


            except IndexError:
                self.GG += 1
                continue

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    iaq = IaqSensor(config, "COM4", 2)
    # iaq.set_task_id("")
    iaq.set_task_mode(True)
    iaq.run()
    print(iaq.get_data())
