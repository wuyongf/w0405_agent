import serial
import time
import threading
import src.top_module.db_top_module as NWDB
from datetime import datetime
import src.utils.methods as umethods
import src.top_module.port as port
import src.top_module.analysis.gyro_after_processing as GAP
import src.top_module.analysis.event_publisher as event_publisher

# Voltage = 5V

# todo:
#   function:
#       1. get data -> return all data
#       2. insert
#       3. stream
#       4. run(collectdata)
#       5. data_store
#       6. get_rules
#       7. check_stack

#       Use Savitzky-Golay filter to filter the noise


class Gyro():

    def __init__(self, modb, config, port_config, status_summary):
        self.sid = port_config.get('GYRO', 'sid')
        self.port = port.port().port_match(self.sid)
        self.baudrate = 115200
        self.ser = serial.Serial(self.port, self.baudrate)
        self.time_interval = 0.05  # Max: 200Hz, time interval = 0.005,  Default = 0.01sec, 100Hz
        # self.modb = NWDB.TopModuleDBHandler(config)
        self.modb = modb
        self.gap = GAP.gyro_after_processing(self.modb, status_summary)
        print("SerialController initialized")
        
        self.status_summary = status_summary
        
        self.acc = []
        self.gyro = []
        self.angle = []
        self.temp = []
        self.pnh = []
        self.command = [0x50, 0x03, 0x00, 0x2D, 0x00, 0x1C, 0xD9, 0x8B]
        self.pack_id = 0
        self.task_id = 0
        self.lift_id = 0
        
        self.stop_event = threading.Event()
        self.run_thread = threading.Thread(target=self.start_collection)
        self.event_publisher = event_publisher.EventPublisher('localhost', status_summary)


    def set_task_id(self, id):
        self.task_id = id
        
    def set_lift_id(self, id):
        self.lift_id = id

    def run(self):
        self.collect_data()
        
    def start(self):
        self.run_thread.start()
        
    def stop(self) :
        self.gap.after_processing(self.pack_id)
        self.stop_event.set()

    def get_acc(self, datahex):
        axh = datahex[0]
        axl = datahex[1]
        ayh = datahex[2]
        ayl = datahex[3]
        azh = datahex[4]
        azl = datahex[5]
        k_acc = 9.81 * 2
        acc_x = (axh << 8 | axl) / 32768.0 * k_acc
        acc_y = (ayh << 8 | ayl) / 32768.0 * k_acc
        acc_z = (azh << 8 | azl) / 32768.0 * k_acc
        if acc_x >= k_acc:
            acc_x -= 2 * k_acc
        if acc_y >= k_acc:
            acc_y -= 2 * k_acc
        if acc_z >= k_acc:
            acc_z -= 2 * k_acc
        return [acc_x, acc_y, acc_z]

    def get_gyro(self, datahex):
        wxh = datahex[0]
        wxl = datahex[1]
        wyh = datahex[2]
        wyl = datahex[3]
        wzh = datahex[4]
        wzl = datahex[5]
        k_gyro = 2000.0
        gyro_x = (wxh << 8 | wxl) / 32768.0 * k_gyro
        gyro_y = (wyh << 8 | wyl) / 32768.0 * k_gyro
        gyro_z = (wzh << 8 | wzl) / 32768.0 * k_gyro
        if gyro_x >= k_gyro:
            gyro_x -= 2 * k_gyro
        if gyro_y >= k_gyro:
            gyro_y -= 2 * k_gyro
        if gyro_z >= k_gyro:
            gyro_z -= 2 * k_gyro
        return [gyro_x, gyro_y, gyro_z]

    def get_angle(self, datahex):
        rxh = datahex[0]
        rxl = datahex[1]
        ryh = datahex[2]
        ryl = datahex[3]
        rzh = datahex[4]
        rzl = datahex[5]
        k_angle = 180.0
        angle_x = (rxh << 8 | rxl) / 32768.0 * k_angle
        angle_y = (ryh << 8 | ryl) / 32768.0 * k_angle
        angle_z = (rzh << 8 | rzl) / 32768.0 * k_angle
        if angle_x >= k_angle:
            angle_x -= 2 * k_angle
        if angle_y >= k_angle:
            angle_y -= 2 * k_angle
        if angle_z >= k_angle:
            angle_z -= 2 * k_angle
        return [angle_x, angle_y, angle_z]

    def get_pnh(self, datahex):
        p0 = datahex[0]
        p1 = datahex[1]
        p2 = datahex[2]
        p3 = datahex[3]
        h0 = datahex[4]
        h1 = datahex[5]
        h2 = datahex[6]
        h3 = datahex[7]
        pressure = ((p2 << 24) | (p3 << 16) | (p0 << 8) | p1)
        height = ((h2 << 24) | (h3 << 16) | (h0 << 8) | h1)
        return pressure, height

    def get_temp(self, datahex):
        temph = datahex[0]
        templ = datahex[1]
        tempval = (temph << 8 | templ)
        temperature = round(tempval / 100, 2)
        return temperature
    
    def set_pack_id(self, id):
        self.pack_id = id
    
    def start_collection(self):
        # create data pack & set pack_id
        self.set_pack_id(self.create_data_pack(task_id=self.task_id, lift_id=self.lift_id))
        # start collect data
        self.collect_data()
        

    def create_data_pack(self, task_id, lift_id):
        # TODO: task_id
        return self.modb.CreateGyroDataPack(task_id=task_id, lift_id=lift_id)

    def insert_data(self, data):
        print("[gyro.py] dataInsert")
        list_to_str = ','.join([str(elem) for elem in data])
        self.modb.InsertGyroChunk(pack_id=self.pack_id, accel_z=list_to_str)

    def collect_data(self):
        if self.ser and self.ser.is_open:
            collected_data = []
            while not self.stop_event.is_set():
                send_data = serial.to_bytes(self.command)
                self.ser.write(send_data)
                time.sleep(self.time_interval)
                len_return_data = self.ser.inWaiting()

                if len_return_data:
                    return_data = self.ser.read(len_return_data)
                    return_data_arr = bytearray(return_data)
                    # empty arrays for temporally data transition
                    self.acc = []
                    self.gyro = []
                    self.angle = []
                    self.temp = []
                    self.pnh = []

                    count = 1
                    for data in return_data_arr:
                        if 18 <= count <= 23:  # get acc data
                            self.acc.append(data)
                        if 24 <= count <= 29:  # get gyro data
                            self.gyro.append(data)
                        if 36 <= count <= 41:  # get angle data
                            self.angle.append(data)
                        if 42 <= count <= 43:  # get temperature data
                            self.temp.append(data)
                        if 52 <= count <= 59:  # get pnh data
                            self.pnh.append(data)
                        count += 1

                    result = self.get_motion_data()
                    result_acc_z = round(result[0][2],2)
                    
                    if result_acc_z > 0:
                        collected_data.append(result_acc_z)
                        if self.stop_event.is_set():
                            print('finish, Upload immediately')
                            # insert to datachunk
                            self.insert_data(data=collected_data)
                            # clear data stack
                            collected_data = []
                            break
       
                        if len(collected_data) > 200:
                            # insert to datachunk
                            self.insert_data(data=collected_data)
                            # clear data stack
                            collected_data = []
                    
                    # print(collected_data)

    def print_data(self):
        print(datetime.now())
        # print(self.get_acc(self.acc))
        print("acc-x: " + str(round(self.get_acc(self.acc)[0], 2)))
        print("acc-y: " + str(round(self.get_acc(self.acc)[1], 2)))
        print("acc-z: " + str(round(self.get_acc(self.acc)[2], 2)))  #acc-z
        print("gyro-wx: " + str(round(self.get_gyro(self.gyro)[0], 2)))
        print("gyro-wy: " + str(round(self.get_gyro(self.gyro)[1], 2)))
        print("gyro-wz: " + str(round(self.get_gyro(self.gyro)[2], 2)))
        print("angle-rx: " + str(round(self.get_angle(self.angle)[0], 2)))
        print("angle-ry: " + str(round(self.get_angle(self.angle)[1], 2)))
        print("angle-rz: " + str(round(self.get_angle(self.angle)[2], 2)))

    def get_motion_data(self):
        return [self.get_acc(self.acc), self.get_gyro(self.gyro), self.get_angle(self.angle)]

    # def get_acc_data(self):
    #     return self.get_acc(self.acc)


if __name__ == '__main__':
    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 105.40159891291846, "y": 67.38314149752657, "theta": 75.20575899303867}, "map_id": 2, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status
    # Example usage:
    
    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = NWDB.TopModuleDBHandler(config, status_summary)

    gyro = Gyro(modb, config, port_config, status_summary)
    # gyro.collect_data()
    # gyro.start_collection()
    gyro.start()
    time.sleep(20)
    gyro.stop()