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
        self.header_list_insert = ["co2", "tvoc", "hcho", "pm25", "rh", "temperature", "pm10",
                                   "pm1", "lux", "mcu_temperature", "db", "pos_x", "pos_y", "pos_theta", "map_id"]
        self.header_list = ["co2", "tvoc", "hcho", "pm25", "rh",
                            "temperature", "pm10", "pm1", "lux", "mcu_temperature", "db"]
        # self.modb = NWDB.TopModuleDBHandler(config)
        self.modb = modb
        self.data_stack = []
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.collect_data)
        self.stream_run_thread = threading.Thread(target=self.stream_thread)
        self.movement_run_thread = threading.Thread(target=self.check_movement_thread)
        self.status_summary = status_summary
        self.user_rules = rule.UserRulesChecker(self.modb, self.header_list_insert, status_summary)
        # Result
        self.result = []
        self.result_insert_array = []
        self.result_check_array = []
        # Robot displacement
        self.capture_x = 0
        self.capture_y = 0
        self.displacement = 0

    def run(self):
        self.collect_data()

    def start(self):
        self.run_thread.start()
        self.stream_run_thread.start()
        self.movement_run_thread.start()

    def stop(self):
        self.stop_event.set()

    def get_current_postition(self):
        obj = json.loads(self.status_summary())
        x = obj["position"]["x"]
        y = obj["position"]["y"]
        return x, y

    def set_capture_position(self, x, y):
        self.capture_x = x
        self.capture_y = y

    def reset_displacement(self):
        self.displacement = 0

    def get_data(self, datahex):
        co2 = (datahex[0] << 8 | datahex[1]) 
        tvoc = (datahex[2] << 8 | datahex[3])
        ch2o = (datahex[4] << 8 | datahex[5])
        pm25 = (datahex[6] << 8 | datahex[7])
        humi = (datahex[8] << 8 | datahex[9]) / 100
        temp = (datahex[10] << 8 | datahex[11]) / 100 - 5.5
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
        # print("[iaq.py] dataStream")
        # print(f'[iaq.py] dataStream: value: {value}')
        self.modb.StreamIaqData("sensor.iaq.stream", self.header_list, value)
        # self.modb.DeleteLastStreamIaqData()

    def set_task_mode(self, e, task_id=0):
        # Set task mode
        self.task_mode = e

        # ***** BUG Here : This will set task_id = 0 before upload data to db
        # self.task_id = task_id

        if e is True:
            # Set current position for calculate displacement
            x, y = self.get_current_postition()
            self.set_capture_position(x, y)
            print(f"[iaqV2.py] Start task mode, set current x,y = ({x}, {y})")

        # Upload to db & check user rules when IAQ task = OFF
        if e is False:
            print('[iaqV2.py]: Stop IAQ task, Insert data to db')
            self.insert_array_to_db()
            self.data_check_array()
            self.result_insert_array = []
            self.result_check_array = []
        # Debug 06/11/2023 : Move set id to end of uploading
        self.task_id = task_id

    def data_check_stack(self, dataset):
        self.data_stack.append(dataset)
        if len(self.data_stack) >= 5:
            # self.check_stack(self.data_stack)
            # NOTE: *** Check the data with user define rules ***
            # print(self.data_stack)
            self.user_rules.check_stack(self.data_stack, self.task_id)
            # clear the stack
            self.data_stack.clear()

    def get_rules_column(self, dataset, column):
        return [i.get(column) for i in dataset]

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
                    if len(list(rawdata)) != 22:
                        continue

                    result = self.get_data(rawdata)
                    # self.result = result

                    if sum(result) < 30000 and result[2] < 5000:
                        if self.task_mode:
                            # self.insert_result(result)
                            self.insert_result_toArray(result)

                        self.result = result
                        time.sleep(self.time_interval)

                except IndexError:
                    self.GG += 1
                    continue

    def insert_result(self, result):
        # Insert result to mySQL
        result_insert = result.copy()
        result_check = result.copy()
        result_insert = self.append_robot_position(result_insert)
        result_check = self.append_robot_position(result_check, xyonly=True)
        self.data_check_stack(result_check)
        # print(result)
        self.data_insert(result_insert)
        print(f"[iaq.py] Task ID: {self.task_id}")

    def insert_result_toArray(self, result):
        # Insert result to mySQL
        result_insert = result.copy()
        result_check = result.copy()
        result_insert = self.append_robot_position(result_insert)
        result_check = self.append_robot_position(result_check, xyonly=True)

        # Avoid any upload to db during inspection
        # self.data_check_stack(result_check)
        # self.data_insert(result_insert)

        # Insert result to local array
        self.result_insert_array.append(result_insert)
        self.result_check_array.append(result_check)

    def insert_array_to_db(self):
        for i in self.result_insert_array:
            self.data_insert(i)

    def data_check_array(self):
        for i in self.result_check_array:
            self.data_check_stack(i)

    def check_movement_thread(self):
        while True:
            if self.task_mode is True:
                self.displacement = self.get_robot_displacement()
                print("[iaqV2] displacement: ", self.displacement)
                self.update_capture_position()
            # time.sleep(0.5)
            time.sleep(2)

    def get_robot_displacement(self):
        current_x, current_y = self.get_current_postition()
        delta_x = current_x - self.capture_x
        delta_y = current_y - self.capture_y
        displacement = (delta_x ** 2 + delta_y ** 2) ** 0.5
        return displacement

    def update_capture_position(self):
        current_x, current_y = self.get_current_postition()
        self.set_capture_position(x=current_x, y=current_y)

    def stream_thread(self):
        while(True):
            self.data_stream(self.result)
            # print(f'[iaqv2.stream_thread]: self.result: {self.result}')
            time.sleep(self.time_interval)

    def parse_json(self):
        obj = json.loads(self.status_summary())
        # print(obj["position"]["x"])
        # print(obj["position"]["y"])
        return obj

    def append_robot_position(self, array, xyonly=False):
        obj = json.loads(self.status_summary())
        array.append(obj["position"]["x"])
        array.append(obj["position"]["y"])

        # set capture position
        x = obj["position"]["x"]
        y = obj["position"]["y"]
        self.set_capture_position(x, y)

        if xyonly is False:
            array.append(obj["position"]["theta"])
            array.append(obj["map_id"])
        return array


if __name__ == '__main__':
    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 1520, "y": 761, "theta": 75.20575899303867}, "map_id": 7, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status

    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = NWDB.TopModuleDBHandler(config, status_summary)

    iaq = IaqSensor(modb, config, port_config, status_summary, 2)
    print(iaq.parse_json())
    # iaq.set_task_id("")
    iaq.start()
    # # time.sleep(5)
    iaq.set_task_mode(True, task_id=-1)
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
