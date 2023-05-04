import serial
import time
import threading
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
        self.task_id = ""
        self.column_items = ["co2", "tvoc", "hcho", "pm25", "rh", "temperature", "pm10", "pm1", "lux", "mcu_temperature", "db"]
        self.nwdb = NWDB.robotDBHandler(config)
        self.data_stack = []
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.collect_data)


    def run(self):
        self.collect_data()
        
    def start(self):
        self.run_thread.start()
        
    def stop(self) :
        self.stop_event.set()


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

    def set_task_mode(self, e, taskid=""):
        self.task_mode = e
        self.task_id = taskid
        print(self.task_mode)

    def data_check_stack(self, dataset):
        self.data_stack.append(dataset)
        if len(self.data_stack) >= 5:
            self.check_stack(self.data_stack)
            # clear the stack
            self.data_stack.clear()

    def get_rules_column(self, dataset, column):
        return [i.get(column) for i in dataset]

    # NOTE: *** Check the data with user define rules ***
    def check_stack(self, data_stack):
        # mySQL get (type, threshold, limit_type) as list
        rules_list = self.nwdb.GetUserRules()
        print(rules_list)
        rules_type_list = self.get_rules_column(rules_list, "data_type")
        rules_threshold_list = self.get_rules_column(rules_list, "threshold")
        rules_limit_type_list = self.get_rules_column(rules_list, "limit_type")
        rules_name_list = self.get_rules_column(rules_list, "name")

        for data in data_stack:
            for row_num, data_type in enumerate(rules_type_list):
                try:
                    # Compare with rules_type_list, find the index of data
                    col_idx = self.column_items.index(data_type)
                    threshold = rules_threshold_list[row_num]
                    limit_type = rules_limit_type_list[row_num]
                    name = rules_name_list[row_num]
                    value = data[col_idx]
                    
                    print(f"Checking: {value}, Rule Name: {name}, Data Type: {data_type}, Column Index: {col_idx}, Limit Type: {limit_type}, Threshold: {threshold}")

                    if limit_type == "HIGH" and value > threshold:
                        print(f"*** Higher than threshold, Rule Name: {name}, Type: {data_type}, Threshold: {threshold}, Value: {value}")

                    elif limit_type == "LOW" and value < threshold:
                        print(f"*** Lower than threshold, Rule Name: {name}, Type: {data_type}, Threshold: {threshold}, Value: {value}")

                except ValueError:
                    print(f"No matched data type for rule data type {data_type}")



    def collect_data(self):
        with serial.Serial(self.port, self.bandwidth) as ser:
            while not self.stop_event.is_set():
                try:
                    named_tuple = time.localtime()  # get struct_time
                    time_string = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)

                    if not ser.is_open:
                        continue
                    
                    send_data = serial.to_bytes(self.command)
                    ser.write(send_data)  # 发送命令
                    time.sleep(0.1)  # 延时，否则len_return_data将返回0，此处易忽视！！！
                    
                    len_return_data = ser.inWaiting()  # 获取缓冲数据（接收数据）长度
                    if not len_return_data:
                        continue

                    return_data = ser.read(len_return_data)  # 读取缓冲数据
                    return_data_arr = bytearray(return_data)
                    count = 1
                    # print(return_data_arr)
                    
                    rawdata = [data for i, data in enumerate(return_data_arr) if 4 <= i + 1 <= 25]
                    result = self.get_data(rawdata)
                    print(result)

                    if sum(result) < 30000:

                        if self.task_mode:
                            # Insert to mySQL
                            # print('***********taskmode  ON**********')
                            self.data_check_stack(result)
                            self.data_insert(result)
                            print(f"Task ID: {self.task_id}")

                        # Stream to mySQL
                        self.data_stream(result)
                        time.sleep(self.time_interval)


                except IndexError:
                    self.GG += 1
                    continue

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    iaq = IaqSensor(config, "COM3", 2)
    # iaq.set_task_id("")
    iaq.start()
    
    time.sleep(10)
    iaq.set_task_mode(True, "Place task_id Here")
    
    time.sleep(10)
    # second argument (task id) is optional
    iaq.set_task_mode(False)
    
    time.sleep(10)
    # Stop the thread
    iaq.stop()
