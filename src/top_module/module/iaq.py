import serial
import time
import threading
import json
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods
import src.top_module.analysis.user_rules as rule
import src.top_module.port as port

class IaqSensor():
    def __init__(self, modb, config, port_config, status_summary, Ti):
        self.sid = port_config.get('IAQ', 'sid')
        self.port = port.port().port_match(self.sid)
        self.bandwidth = '9600'
        self.count = 0
        self.GG = 0
        self.time_interval = Ti
        self.command = [0x01, 0x03, 0x00, 0x00, 0x00, 0x0B, 0x04, 0x0D]
        self.task_mode = 0
        self.task_id = 0
        self.header_list_insert = ["co2", "tvoc", "hcho", "pm25", "rh", "temperature", "pm10", "pm1", "lux", "mcu_temperature", "db", "pos_x", "pos_y", "pos_theta", "map_id"]
        self.header_list = ["co2", "tvoc", "hcho", "pm25", "rh", "temperature", "pm10", "pm1", "lux", "mcu_temperature", "db"]
        # self.modb = NWDB.TopModuleDBHandler(config)
        self.modb = modb
        self.data_stack = []
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.collect_data)
        self.status_summary = status_summary
        self.user_rules = rule.UserRulesChecker(self.modb, self.header_list_insert, status_summary)

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
        # print(f'normal len: {len(list(datahex))}')
        return [co2, tvoc, ch2o, pm25, humi, temp, pm10, pm01, lux, mcu_temp, db]       

    def data_insert(self, value):
        print("[iaq.py] dataInsert")
        self.modb.InsertIaqData("sensor.iaq.history", self.header_list_insert, value, self.task_id)

    def data_stream(self, value):
        print("[iaq.py] dataStream")
        self.modb.StreamIaqData("sensor.iaq.stream", self.header_list, value)
        self.modb.DeleteLastStreamIaqData()

    def set_task_mode(self, e, task_id=0):
        # self.event_publisher.publish_test()
        # print(self.status_summary())
        # self.publish_event(value=10, name= 'name', data_type= 'data_type', threshold=10)
        
        self.task_mode = e
        self.task_id = task_id
        print(self.task_mode)

    

    def data_check_stack(self, dataset):
        self.data_stack.append(dataset)
        if len(self.data_stack) >= 20:
            # self.check_stack(self.data_stack)
            # NOTE: *** Check the data with user define rules ***
            self.user_rules.check_stack(self.data_stack)
            # clear the stack
            self.data_stack.clear()

    def get_rules_column(self, dataset, column):
        return [i.get(column) for i in dataset]

    # NOTE: *** Check the data with user define rules ***
    # def check_stack(self, data_stack):
        # mySQL get (type, threshold, limit_type) as list
        rules_list = self.modb.GetUserRules()
        print(rules_list)
        rules_type_list = self.get_rules_column(rules_list, "data_type")
        rules_threshold_list = self.get_rules_column(rules_list, "threshold")
        rules_limit_type_list = self.get_rules_column(rules_list, "limit_type")
        rules_name_list = self.get_rules_column(rules_list, "name")

        for data in data_stack:
            for row_num, data_type in enumerate(rules_type_list):
                try:
                    # Compare with rules_type_list, find the index of data
                    col_idx = self.header_list.index(data_type)
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
                    
                    if len(list(rawdata)) != 22: continue
                    result = self.get_data(rawdata)
                    print(result)
                    

                    # print(result_insert)

                    if sum(result) < 30000 and result[2] < 5000 :
                        if self.task_mode:
                            # Insert to mySQL
                            # print('***********taskmode  ON**********')
                            result_insert = result.copy()
                            result_insert = self.append_robot_position(result_insert)
                            self.data_check_stack(result)
                            self.data_insert(result_insert)
                            print(f"[iaq.py] Task ID: {self.task_id}")

                        # Stream to mySQL
                        self.data_stream(result)
                        time.sleep(self.time_interval)


                except IndexError:
                    self.GG += 1
                    continue

    def parse_json(self):
        obj = json.loads(self.status_summary())
        # print(obj["position"]["x"])
        # print(obj["position"]["y"])
        return obj

    def append_robot_position(self, array):
        obj = json.loads(self.status_summary())
        array.append(obj["position"]["x"])
        array.append(obj["position"]["y"])
        array.append(obj["position"]["theta"])
        array.append(obj["map_id"])
        return array


if __name__ == '__main__':
    def status_summary():
        status = '{"battery": 10.989, "position": {"x": 0.0, "y": 0.0, "theta": 0.0}, "map_id": 7}'
        return status
    
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = NWDB.TopModuleDBHandler(config, status_summary)


    iaq = IaqSensor(modb, config, port_config, status_summary, 2)
    print(iaq.parse_json())
    # iaq.set_task_id("")
    iaq.start()
    # # time.sleep(5)
    iaq.set_task_mode(True, task_id = 999)
    # iaq.set_task_mode(False)
    # # 
    time.sleep(1800)
    # second argument (task id) is optional

    # time.sleep(10)

    # iaq.set_task_mode(True, 6)
    # # 
    # time.sleep(10)
    # # second argument (task id) is optional
    # iaq.set_task_mode(False)

    
    # time.sleep(10)
    # Stop the thread
    # iaq.stop()
