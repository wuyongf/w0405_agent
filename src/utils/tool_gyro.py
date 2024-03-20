import datetime
from src.utils.methods import load_config, convert_list2txt
from src.models.db_robot import robotDBHandler
class GyroTool:
    def __init__(self,):
        self.save_folder = None
        pass

def get_gyro_info_durations(video_start_date, trimmed_gyro_info):
    gyro_info_durations = []
    video_start_timestamp = video_start_date.timestamp()
    gyro_start_timestamp = trimmed_gyro_info[0][1].timestamp()
    offset_timestamp = gyro_start_timestamp - video_start_timestamp
    for idx, created_date in enumerate(trimmed_gyro_info):
        current_timestamp = created_date[1].timestamp() + offset_timestamp
        current_seconds = current_timestamp - gyro_start_timestamp
        gyro_info_durations.append([trimmed_gyro_info[idx][0], current_seconds])
    return gyro_info_durations

def trim_gyro_info(video_start_date, video_duration, compact_gyro_info):
    # video_start_date = #datetime.datetime(2024, 3, 18, 19, 34, 56)
    # video_duration = 164
    video_end_date = video_start_date + datetime.timedelta(seconds=video_duration)
    print(video_end_date)

    output_gyro_info = []
    for idx, gyro_info in enumerate(compact_gyro_info):
        if(video_start_date > gyro_info[1]): continue
        elif(video_end_date < gyro_info[1]): continue
        else:
            output_gyro_info.append(gyro_info)
    return output_gyro_info

if __name__ == '__main__':
    config = load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)

    task_id = 539

    pack_id = nwdb.get_value_with_conditions('sensor.gyro.datapack', 'ID', {'task_id': task_id + 1})[0]
    print(pack_id)

    accel_z = nwdb.get_value_with_conditions('sensor.gyro.datachunk', 'accel_z', {'pack_id': pack_id})
    print(accel_z)

    created_dates = nwdb.get_value_with_conditions('sensor.gyro.datachunk', 'created_date', {'pack_id': pack_id})
    print(created_dates)

    compact_gyro_info = [[x, y] for x, y in zip(accel_z, created_dates)]
    print(f'len(compact_gyro_info): {len(compact_gyro_info)}')

    video_start_date = datetime.datetime(2024, 3, 18, 19, 32, 4)
    video_duration = 164
    trimmed_gyro_info = trim_gyro_info(video_start_date, video_duration, compact_gyro_info)

    gyro_info_duration = get_gyro_info_durations(video_start_date, trimmed_gyro_info)
    print(gyro_info_duration) 

    # Save the results to a file
    convert_list2txt(list = gyro_info_duration, output_file_dir = 'gyro_compact_info.txt')
    # output_file_dir = 'gyro_compact_info.txt'
    # with open(output_file_dir, 'w') as output_file:
    #     for idx, result in enumerate(gyro_info_duration):
    #         if(idx is len(compact_gyro_info)-1): output_file.write(str(result))
    #         else:output_file.write(str(result) + '\n')