import datetime
import numpy as np
from src.models.db_robot import robotDBHandler
from src.utils.methods import load_config, convert_list2txt
from src.utils.gyro_analyzer import GyroAnalyzer

class GyroTool:
    '''
    Workflow: 
    1. Retrieve raw_gyro_data from nwdb
    2. Trim raw_gyro_data according to video, return gyro_compact_info
    3. Get time_array and gyro_array for Data Analysis
    4. 
    '''
    def __init__(self, config):
        self.temp_folder = None
        self.nwdb = robotDBHandler(config)
        self.ga = GyroAnalyzer()
        #
        self.db_gyro_raw_info = None
        self.gyro_synced_info = None
        self.gyro_compact_info = None

    def set_temp_dir(self, dir):
        self.temp_folder = dir

    def get_db_gyro_raw_info(self, task_id):
        ## Retrieve raw_gyro_data from nwdb
        pack_id = self.nwdb.get_value_with_conditions('sensor.gyro.datapack', 'ID', {'task_id': task_id + 1})[0]
        accel_z = self.nwdb.get_value_with_conditions('sensor.gyro.datachunk', 'accel_z', {'pack_id': pack_id})
        created_dates = self.nwdb.get_value_with_conditions('sensor.gyro.datachunk', 'created_date', {'pack_id': pack_id})
        self.db_gyro_raw_info = [[x, y] for x, y in zip(accel_z, created_dates)]
        # print(f'len(raw_db_gryo_info): {len(self.raw_db_gryo_info)}')
        return self.db_gyro_raw_info

    def sync_gyro_info_with_video(self, video_start_date_str, video_duration, raw_gyro_info):
        video_start_date = datetime.datetime.strptime(video_start_date_str, '%Y-%m-%d %H:%M:%S')
        video_end_date = video_start_date + datetime.timedelta(seconds=video_duration)
        # print(video_end_date)
        self.gyro_synced_info = []
        for idx, gyro_info in enumerate(raw_gyro_info):
            if(video_start_date > gyro_info[1]): 
                # print(f'skip1')
                continue
            elif(video_end_date < gyro_info[1]): 
                # print(f'skip2')
                continue
            else:
                self.gyro_synced_info.append(gyro_info)
        return self.gyro_synced_info

    def get_gyro_compact_info(self, video_start_date_str, gyro_synced_info):
        self.gyro_compact_info = []
        video_start_date = datetime.datetime.strptime(video_start_date_str, '%Y-%m-%d %H:%M:%S')
        video_start_timestamp = video_start_date.timestamp()
        gyro_start_timestamp = gyro_synced_info[0][1].timestamp()
        offset_timestamp = gyro_start_timestamp - video_start_timestamp
        for idx, created_date in enumerate(gyro_synced_info):
            current_timestamp = created_date[1].timestamp() + offset_timestamp
            current_seconds = current_timestamp - gyro_start_timestamp
            self.gyro_compact_info.append([gyro_synced_info[idx][0], current_seconds])
        return self.gyro_compact_info

if __name__ == '__main__':
    config = load_config('../../conf/config.properties')
    gt = GyroTool(config)
    # nwdb = robotDBHandler(config)
    db_gyro_raw_info = gt.get_db_gyro_raw_info(task_id = 539)

    ## Align raw_gryo_data with video duration
    video_start_date = datetime.datetime(2024, 3, 18, 19, 32, 4)
    video_duration = 164
    # video_start_date = datetime.datetime(2024, 3, 18, 19, 3, 21)
    # video_duration = 166
    gyro_synced_info = gt.sync_gyro_info_with_video(video_start_date, video_duration, db_gyro_raw_info)
    gyro_compact_info = gt.get_gyro_compact_info(video_start_date, gyro_synced_info)
    print(gyro_compact_info)

    # Save the results to a file
    gyro_compact_info_dir = gt.temp_folder + '/gyro_compact_info.txt'
    gyro_compact_info_dir = convert_list2txt(list = gyro_compact_info, output_file_dir = 'gyro_compact_info.txt')

    # Start Analysing
    descrete_gyro_data = gt.ga.load_gyro_compact_info(gyro_compact_info_dir)
    time_array, gyro_data = gt.ga.algin_gyro_with_timestampe(gt.ga.descrete_gyro_data)
    smoothed_gyro_data = gt.ga.smmoth_gyro_data(gyro_data, window_length=81, polyorder=7)
    
    sliced_gyro_data = gt.ga.slice_gyro_data(start_sec=9.382, end_sec=27.217, gyro_data=smoothed_gyro_data)
    res = gt.ga.get_acc_direction(sliced_gyro_data)
    print(res)


