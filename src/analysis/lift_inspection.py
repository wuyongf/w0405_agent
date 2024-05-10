import os
from pathlib import Path
from src.utils.methods import load_config, convert_list2txt
from src.utils.tool_gyro  import GyroTool
from src.utils.tool_audio import AudioTool
from src.utils.tool_video import VideoTool
from src.utils.door_status_analyzer import DoorStatusAnalyzer
from src.utils.methods import convert_timestamp2date
from src.models.enums.nw import CameraPosition, LiftStatus
from src.models.enums.azure import ContainerName as AzureContainerName
from src.models.db_robot import robotDBHandler
from src.handlers.azure_blob_handler import AzureBlobHandler


class LiftInsectionAnalyser:
    def __init__(self, config, nwdb: robotDBHandler):
        self.temp_folder_dir = None
        self.preprocess_folder_dir = None
        
        #raw_data
        self.raw_data_folder_dir = None
        self.raw_audio_dir = None
        self.raw_front_video_dir = None
        self.raw_rear_video_dir = None

        #temp_data
        self.mono_audio_dir = None

        #data
        self.task_id = 0

        #tools
        self.nwdb = nwdb
        self.config = config
        self.blob_handler  = AzureBlobHandler(config)
        self.gyro_tool  = GyroTool(config)
        self.audio_tool = AudioTool()
        self.video_tool = VideoTool()
        self.dsa = DoorStatusAnalyzer()

        ### configuration
        self.robot_id = 1
        ## [nwdb data integration]
        self.audio_mission_id = 0
        self.gyro_task_id = 0
        self.raw_audio_name = None
        self.door_compact_statuses_info_dir = None
        self.lift_status_dir = None
        ## [azure]
        self.foreground_file_dir = None
        self.background_file_dir = None
        self.raw_video_frame_dir = None
        self.mp3_raw_audio_dir = None
        self.mp3_foreground_file_dir = None
        self.mp3_background_file_dir = None
        # self.raw_audio_dir 

        # table 'ai.lift_inspection.audio.analysis'


    def set_robot_id(self, robot_id):
        self.robot_id = robot_id

    def set_raw_data_dir_path(self, audio_dir, front_video_dir, rear_video_dir):
        self.raw_audio_dir = audio_dir
        self.raw_front_video_dir = front_video_dir
        self.raw_rear_video_dir = rear_video_dir

        self.raw_audio_path = Path(audio_dir)
        self.raw_front_video_path = Path(front_video_dir)
        self.raw_rear_video_path = Path(rear_video_dir)    

        ## [nwdb data integration]
        self.raw_audio_name = self.raw_audio_path.name    
        pass

    def set_temp_dir(self, temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        self.temp_folder_dir = temp_dir
        self.audio_tool.set_temp_dir(temp_dir)
        self.video_tool.set_temp_dir(temp_dir)
        self.gyro_tool.set_temp_dir(temp_dir)
    
    def set_task_id(self, task_id):
        self.task_id = task_id

        ## [nwdb data integration]
        self.audio_mission_id = self.task_id
        self.gyro_task_id = self.task_id + 1

    # [Workflow]
    def get_raw_data_duration(self,):
        self.front_video_duration = self.video_tool.get_video_duration(self.raw_front_video_dir)
        self.front_video_start_timestamp = float(self.raw_front_video_path.stem.split('_')[-1])
        self.front_video_end_timestamp = self.front_video_start_timestamp + self.front_video_duration
        self.front_video_start_date = convert_timestamp2date(self.front_video_start_timestamp)
        self.front_video_end_date = convert_timestamp2date(self.front_video_end_timestamp)

        self.audio_end_timestamp = float(self.raw_audio_path.stem.split('_')[-1])
        self.audio_duration = self.audio_tool.get_audio_duration(self.raw_audio_dir)
        self.audio_start_timestamp = self.audio_end_timestamp - self.audio_duration
        self.audio_start_date = convert_timestamp2date(self.audio_start_timestamp)
        self.audio_end_date = convert_timestamp2date(self.audio_end_timestamp)
        
        rear_video_duration = self.video_tool.get_video_duration(self.raw_rear_video_dir)

        print(f'[get_raw_data_duration] front_video_start_date: {self.front_video_start_date}')
        print(f'[get_raw_data_duration] front_video_end_date:   {self.front_video_end_date}')
        print(f'[get_raw_data_duration] front_video_duration:   {self.front_video_duration}')
        print(f'[get_raw_data_duration] audio_start_date: {self.audio_start_date}')
        print(f'[get_raw_data_duration] audio_end_date:   {self.audio_end_date}')
        print(f'[get_raw_data_duration] audio_duration:   {self.audio_duration}')
        pass

    def preprocess_raw_audio(self):
        # front_video_duration = self.video_tool.get_video_duration(self.raw_front_video_dir)
        # front_video_start_timestamp = float(self.raw_front_video_path.stem.split('_')[-1])
        # front_video_end_timestamp = front_video_start_timestamp + front_video_duration
        # audio_end_timestamp = float(self.raw_audio_path.stem.split('_')[-1])
        # audio_duration = self.audio_tool.get_audio_duration(self.raw_audio_dir)
        # audio_start_timestamp = audio_end_timestamp - audio_duration

        # front_video_start_date = convert_timestamp2date(front_video_start_timestamp)
        # front_video_end_date = convert_timestamp2date(front_video_end_timestamp)
        # audio_end_date = convert_timestamp2date(audio_end_timestamp)
        
        # Exception
        if(self.audio_duration < self.front_video_duration):
            print(f'[LiftInsectionTool] audio_duration is less than front_video_duration')
            print(f'[LiftInsectionTool] please check recording files...')
            # return False 
        if(self.front_video_end_timestamp >= self.audio_end_timestamp):
            print(f'[LiftInsectionTool] audio_end_timestamp is less than front_video_end_timestamp')
            print(f'[LiftInsectionTool] please check recording procedure...')
            # return False   
        
        audio_actual_end_timestamp = self.front_video_end_timestamp
        audio_actual_duration = self.front_video_duration
        trim_sec_from_end = self.audio_end_timestamp - self.front_video_end_timestamp

        trim_sec_from_start = self.front_video_start_timestamp - self.audio_start_timestamp

        trimmed_audio_dir = self.audio_tool.trim_audio(self.raw_audio_dir, start_sec=trim_sec_from_start, end_sec=trim_sec_from_start+self.front_video_duration)
        stereo_audio_dir = self.audio_tool.convert_to_stereo_audio(trimmed_audio_dir)
        self.foreground_file_dir, self.background_file_dir = self.audio_tool.separate_audio(stereo_audio_dir)
        self.mono_audio_dir = self.audio_tool.convert_to_mono_audio(self.foreground_file_dir) # mono_audio will be used for model training and inference
        self.mp3_raw_audio_dir = self.audio_tool.convert_to_mp3_raw(trimmed_audio_dir) # mp3 file will be uploaded to cloud

        # print(f'[LiftInsectionTool] front_video_duration: {front_video_duration}')
        # print(f'[LiftInsectionTool] front_video_start_tiemstamp:  {front_video_start_timestamp}')
        # print(f'[LiftInsectionTool] front_video_end_tiemstamp: {front_video_end_timestamp}') 
        # print(f'[LiftInsectionTool] audio_end_timestamp:       {audio_end_timestamp}')
        # print(f'[LiftInsectionTool] front_video_start_date:  {front_video_start_date}')    
        # print(f'[LiftInsectionTool] front_video_end_date:  {front_video_end_date}')       
        # print(f'[LiftInsectionTool] audio_end_date:  {audio_end_date}') 

        return self.mono_audio_dir

    def preprocess_raw_rear_video(self):
        predicted_video_dir, predicted_video_frames_dir, door_sliced_classes_dir, self.raw_video_frame_dir = self.dsa.yolov8_detect_door_status()
        self.dsa.dsq.set_sliced_classes_dir(door_sliced_classes_dir)
        sliced_statuses = self.dsa.dsq.convert_classids2sliced_statuses()
        compact_statuses, compact_statuses_info = self.dsa.dsq.group_sliced_statuses(sliced_statuses)
        compact_door_statuses_info, door_compact_statuses_info_dir = self.dsa.dsq.analyze_door_sequence(compact_statuses, compact_statuses_info)
        # print(compact_door_statuses_info)
        return door_compact_statuses_info_dir
    
    def preprocess_gyro(self):
        db_gyro_raw_info = self.gyro_tool.get_db_gyro_raw_info(self.task_id)

        ## Align raw_gryo_data with video duration
        gyro_synced_info = self.gyro_tool.sync_gyro_info_with_video(self.front_video_start_date, self.front_video_duration, db_gyro_raw_info)
        gyro_compact_info = self.gyro_tool.get_gyro_compact_info(self.front_video_start_date, gyro_synced_info)
        # print(gyro_compact_info)

        # Save the results to a file
        gyro_compact_info_dir = self.gyro_tool.temp_folder + '/gyro_compact_info.txt'
        gyro_compact_info_dir = convert_list2txt(list = gyro_compact_info, output_file_dir = gyro_compact_info_dir)

        # Start Analysing
        descrete_gyro_data = self.gyro_tool.ga.load_gyro_compact_info(gyro_compact_info_dir)
        time_array, gyro_data = self.gyro_tool.ga.algin_gyro_with_timestampe(self.gyro_tool.ga.descrete_gyro_data)
        smoothed_gyro_data = self.gyro_tool.ga.smmoth_gyro_data(gyro_data, window_length=81, polyorder=7)

        pass

    def trim_audio_for_training(self, audio_dir, statuses_info_dir):
        '''
        trim_audio for model training
        '''
        # Convert compact_status_info to the list "statuses_info"
        statuses_info = self.dissemble_compact_status_info(statuses_info_dir)
        
        # Initialize an empty list to store the lift_status_info
        self.lift_status_info = []

        # trim_audio for model training
        for idx, info in enumerate(statuses_info):
            # get door_status
            status_type = info[0] # 'FullyClose' 'FullyOpen' 'OperatingOpenDoor' 'OperatingCloseDoor'
            status_start_time = info[1]
            status_end_time = info[2]

            # handle each situation
            match status_type:
                case "OperatingOpenDoor": 
                    file_dir = os.path.join(self.audio_tool.pals_door_open, f'{idx:02d}.wav')
                    trimmed_audio_dir = self.audio_tool.trim_audio(audio_dir, status_start_time, status_end_time, preprocessd_file_dir=file_dir)
                case "OperatingCloseDoor":
                    file_dir = os.path.join(self.audio_tool.pals_door_close, f'{idx:02d}.wav')
                    trimmed_audio_dir = self.audio_tool.trim_audio(audio_dir, status_start_time, status_end_time, preprocessd_file_dir=file_dir)
                case "FullyClose": 
                    # gyro up or down
                    sliced_gyro_data = self.gyro_tool.ga.slice_gyro_data(start_sec=status_start_time, end_sec=status_end_time, gyro_data=self.gyro_tool.ga.smoothed_gyro_data)
                    acc_direction = self.gyro_tool.ga.get_acc_direction(sliced_gyro_data)
                    print(acc_direction)
                    if(acc_direction == 'up'):
                        file_dir = os.path.join(self.audio_tool.pals_lift_up, f'{idx:02d}.wav')
                        trimmed_audio_dir = self.audio_tool.trim_audio(audio_dir, status_start_time, status_end_time, preprocessd_file_dir=file_dir)      
                    if(acc_direction == 'down'):
                        file_dir = os.path.join(self.audio_tool.pals_lift_down, f'{idx:02d}.wav')
                        trimmed_audio_dir = self.audio_tool.trim_audio(audio_dir, status_start_time, status_end_time, preprocessd_file_dir=file_dir)
                    pass

            # print(status_type)
            # print(status_start_time)
            # print(status_end_time)
            # print('----')

            # hadnle lift_status
            lift_status = None
            match status_type:
                case "OperatingOpenDoor":  lift_status = LiftStatus.door_open
                case "OperatingCloseDoor": lift_status = LiftStatus.door_close
                case "FullyClose": 
                    if(acc_direction == 'up'):   lift_status = LiftStatus.lift_up
                    if(acc_direction == 'down'): lift_status = LiftStatus.lift_down
                case _:
                    lift_status = LiftStatus.unknown
            self.lift_status_info.append([lift_status.value, status_start_time, status_end_time])

        # print(self.lift_status_info)
        ## Write self.lift_status_info to txt file
        self.lift_status_dir = self.temp_folder_dir + '/lift_status_info.txt'
        lift_status_data = '\n'.join([','.join(map(str, sublist)) for sublist in self.lift_status_info])
        with open(self.lift_status_dir, 'w') as file:
            file.write(lift_status_data)

    def start_analysing(self, mission_id, raw_audio_dir, raw_front_video_dir, raw_rear_video_dir, 
             temp_dir, preprocess_dir, ai_model_ckpt_dir):
        
        self.set_raw_data_dir_path(raw_audio_dir, raw_front_video_dir, raw_rear_video_dir)
        self.set_temp_dir(temp_dir)

        self.audio_tool.set_preprocess_dir(preprocess_dir)
        self.audio_tool.cosntruct_preprocess_folders()

        self.get_raw_data_duration()
        # [1] raw_audio -> temp_audio
        mono_audio_dir = self.preprocess_raw_audio()

        # [2] raw_rear_video -> compact_door_status
        self.dsa.set_ckpt(ai_model_ckpt_dir)
        self.dsa.set_preprocess_folder_dir(preprocess_dir)
        self.dsa.set_temp_folder_dir(temp_dir)
        self.dsa.set_source_video(raw_rear_video_dir)
        self.dsa.set_camera_position(CameraPosition.Rear)
        self.door_compact_statuses_info_dir = self.preprocess_raw_rear_video()

        # [3] raw_gyro_data -> analyzed_gyro_data
        self.set_task_id(mission_id)
        self.preprocess_gyro()

        # [4] compact_door_status + temp_audio => sliced_audio
        self.trim_audio_for_training(mono_audio_dir, self.door_compact_statuses_info_dir)

    def init_from_db(self,mission_id):
        def extract_relative_path(abs_dir):
            # Resolve the absolute path to remove any ".." components
            absolute_dir_resolved = os.path.abspath(abs_dir)
            index = absolute_dir_resolved.find("data/")
            relative_dir = absolute_dir_resolved[index:]
            return relative_dir
        
        ai_model_ckpt_dir = self.config.get('LiftInspection','yolov8_ckpt_dir2')
        print(f'[lift_inspection.py] load yolov8 model dir: {ai_model_ckpt_dir}')
        
        raw_audio_dir = self.nwdb.get_single_value('ai.lift_inspection.task_info','raw_audio_dir','ID',mission_id)
        raw_video_front_dir = self.nwdb.get_single_value('ai.lift_inspection.task_info','raw_video_front_dir','ID',mission_id)
        raw_video_rear_dir = self.nwdb.get_single_value('ai.lift_inspection.task_info','raw_video_rear_dir','ID',mission_id)
        temp_dir = self.nwdb.get_single_value('ai.lift_inspection.task_info','temp_dir','ID',mission_id)
        preprocess_dir = self.nwdb.get_single_value('ai.lift_inspection.task_info','preprocess_dir','ID',mission_id)
        
        raw_audio_dir = extract_relative_path(raw_audio_dir)
        raw_video_front_dir = extract_relative_path(raw_video_front_dir)
        raw_video_rear_dir = extract_relative_path(raw_video_rear_dir)
        temp_dir = extract_relative_path(temp_dir)
        preprocess_dir = extract_relative_path(preprocess_dir)
        
        return mission_id, raw_audio_dir, raw_video_front_dir, raw_video_rear_dir,temp_dir, preprocess_dir, ai_model_ckpt_dir

    '''
    Tools
    '''
    def dissemble_compact_status_info(self, statuses_info_dir):
        '''
        status_type = info[0] # 'FullyClose' 'FullyOpen' 'OperatingOpenDoor' 'OperatingCloseDoor'
        status_start_time = info[1]
        status_end_time = info[2]
        '''
        # Initialize an empty list to store the statuses_info
        statuses_info = []
        with open(statuses_info_dir, 'r') as file:
            for line in file:
                # Strip newline characters and other potential whitespace
                line = line.strip()
                # Split the status and time interval based on the comma
                parts = line.split(', ')
                # The first part is the status, the rest is the time interval
                status = parts[0].strip("[]'")
                start_time = float(parts[1].strip('[]').split(', ')[0])
                end_time = float(parts[2].strip('[]').split(', ')[0])
                # Append the status and time interval as a sublist
                statuses_info.append([status, start_time, end_time])
        return statuses_info
    
    def dissemble_lift_status_info(self, file_dir):
        data = []
        with open(file_dir, 'r') as file:
            lines = file.readlines()
            for line in lines:
                # Split each line by comma and convert values to the appropriate type
                values = line.strip().split(',')
                values = [int(values[0])] + [int(float(value)*1000) for value in values[1:]]
                data.append(values)
        return data

    '''
    Upload to nwdb and azure
    '''
    def update_init(self):
        # self.mp3_raw_audio_dir = self.audio_tool.convert_to_mp3_ver2(self.raw_audio_dir)
        self.mp3_foreground_file_dir = self.audio_tool.convert_to_mp3_ver2(self.foreground_file_dir)
        self.mp3_background_file_dir = self.audio_tool.convert_to_mp3_ver2(self.background_file_dir)

    # update nwdb
    def update_nwdb_analysis_result(self):
        # [1] ai.lift_inspection.audio
        self.nwdb.insert_new_audio_id2(robot_id=self.robot_id, 
                                      mission_id=self.audio_mission_id, 
                                      audio_file_name=self.raw_audio_name, is_abnormal=True, 
                                      gyro_id=self.gyro_task_id)
        images_count = 0
        for img_path in Path(self.raw_video_frame_dir).iterdir():
            images_count +=1
        self.nwdb.update_single_value('ai.lift_inspection.audio', 'images_count', images_count, 'mission_id', self.audio_mission_id)

        # [2] ai.lift_inspection.audio.analysis
        audio_id = self.nwdb.get_latest_audio_id()
        lift_statuses = self.dissemble_lift_status_info(self.lift_status_dir)
        # lift_statuses = self.dissemble_compact_status_info(self.door_compact_statuses_info_dir)
        for i, lift_info in enumerate(lift_statuses):
            # [8, 154700, 166300] means [lift_status.value, start_time, end_time]
            match lift_info[0]:
                case LiftStatus.unknown.value:
                    self.nwdb.insert_new_audio_analysis2(audio_id=audio_id,order=i,
                            audio_type=lift_info[0],start_time=lift_info[1],end_time=lift_info[2],
                            is_error=1)      
                case _:
                    self.nwdb.insert_new_audio_analysis2(audio_id=audio_id,order=i,
                            audio_type=lift_info[0],start_time=lift_info[1],end_time=lift_info[2],
                            is_error=0)                    
        pass

    # upload data to azure
    def upload_azure_analysis_data(self):
        # print(self.raw_audio_dir)
        # print(self.foreground_file_dir)
        # print(self.background_file_dir)
        self.blob_handler.update_container_name(AzureContainerName.LiftInspection_Analysis, folder_name=self.task_id)
        self.blob_handler.upload_blobs(self.mp3_raw_audio_dir)
        self.blob_handler.upload_blobs(self.mp3_foreground_file_dir)
        self.blob_handler.upload_blobs(self.mp3_background_file_dir)
        # images
        self.blob_handler.update_container_name(AzureContainerName.LiftInspection_AnalysisImages, folder_name=self.task_id)
        frame_folder_path = Path(self.raw_video_frame_dir)
        for img_path in frame_folder_path.iterdir():
            self.blob_handler.upload_blobs(img_path)
        pass

if __name__ == '__main__':
    config = load_config('../../conf/config.properties')
    nwdb = robotDBHandler(config)
    lfa = LiftInsectionAnalyser(config, nwdb)

    # Example 4
    mission_id = 708
    info = lfa.init_from_db(mission_id)
    print(info)
    lfa.start_analysing(info[0], info[1], info[2], info[3], 
             info[4], info[5], info[6])
    
    lfa.update_init()
    # lfa.update_nwdb_analysis_result()
    lfa.upload_azure_analysis_data()

    # # EXAMPLE 1
    # lfa.set_raw_data_dir_path(audio_dir='data/lift-inspection/raw-data/20240318/001/recording_1709898801.1256263.wav',
    #                          front_video_dir='data/lift-inspection/raw-data/20240318/001/front_video_1709898640.302843.avi',
    #                          rear_video_dir='data/lift-inspection/raw-data/20240318/001/rear_video_1709898640.608474.avi')
    # lfa.set_temp_dir("data/lift-inspection/temp/20240318/001")

    # lfa.audio_tool.set_preprocess_dir("result/sound")
    # lfa.audio_tool.cosntruct_preprocess_folders()

    # # [1] raw_audio -> temp_audio
    # lfa.get_raw_data_duration()
    # mono_audio_dir = lfa.preprocess_raw_audio()

    # # [2] raw_rear_video -> compact_door_status
    # lfa.dsa.set_ckpt('../ai_module/door_status/ckpt/best.pt')
    # lfa.dsa.set_preprocess_folder_dir('data/lift-inspection/preprocess/'+ '20240318/001/'+"door-status/")
    # lfa.dsa.set_temp_folder_dir('data/lift-inspection/temp/'+ '20240318/001/')
    # lfa.dsa.set_source_video("data/lift-inspection/raw-data/20240318/001/rear_video_1709898640.608474.avi")
    # lfa.dsa.set_camera_position(CameraPosition.Rear)
    # door_compact_statuses_info_dir = lfa.preprocess_raw_rear_video()

    # # [3] raw_gyro_data -> analyzed_gyro_data
    # lfa.set_task_id(516)
    # lfa.preprocess_gyro()

    # # [4] compact_door_status + temp_audio => sliced_audio
    # lfa.trim_audio_for_training(mono_audio_dir, door_compact_statuses_info_dir)

    # # EXAMPLE 2
    # mission_id = 539# src/../utils/ src/analysis
    # raw_audio_dir = '../utils/data/lift-inspection/raw-data/20240318/539/recording_1710761694.0095713.wav'
    # raw_front_video_dir = '../utils/data/lift-inspection/raw-data/20240318/539/front_video_1710761524.8510606.avi'
    # raw_rear_video_dir = '../utils/data/lift-inspection/raw-data/20240318/539/rear_video_1710761525.0664573.avi'
    # temp_dir = "../utils/data/lift-inspection/temp/20240318/539"
    # preprocess_dir = "../utils/data/lift-inspection/preprocess/20240318/539"
    # ai_model_ckpt_dir = '../ai_module/door_status/ckpt/best.pt'

    # lfa.start_analysing(mission_id, raw_audio_dir, raw_front_video_dir, raw_rear_video_dir, 
    #          temp_dir, preprocess_dir, ai_model_ckpt_dir)
    
    # # Example 4
    # mission_id = 555
    # info = lfa.init_from_db(mission_id)
    # print(info)
    # lfa.start_analysing(info[0], info[1], info[2], info[3], 
    #          info[4], info[5], info[6])

    # # EXAMPLE 3
    # lfa.set_raw_data_dir_path(audio_dir='data/lift-inspection/raw-data/20240318/533/recording_1710760164.272739.wav',
    #                          front_video_dir='data/lift-inspection/raw-data/20240318/533/front_video_1710759990.5951543.avi',
    #                          rear_video_dir='data/lift-inspection/raw-data/20240318/533/rear_video_1710759990.7885687.avi')
    # lfa.set_temp_dir("data/lift-inspection/temp/20240318/533")

    # # [1] raw_audio -> temp_audio
    # mono_audio_dir = lfa.preprocess_raw_audio()

    # # [2] raw_rear_video -> compact_door_status
    # lfa.dsa.set_ckpt('../ai_module/door_status/ckpt/best.pt')
    # lfa.dsa.set_preprocess_folder_dir('data/lift-inspection/preprocess/'+ '20240318/533/'+"door-status/")
    # lfa.dsa.set_temp_folder_dir('data/lift-inspection/temp/'+ '20240318/533/')
    # lfa.dsa.set_source_video("data/lift-inspection/raw-data/20240318/533/rear_video_1710759990.7885687.avi")
    # lfa.dsa.set_camera_position(CameraPosition.Rear)
    # door_compact_statuses_info_dir = lfa.preprocess_raw_rear_video()

    # # [3] compact_door_status + temp_audio => sliced_audio
    # # ...
    


    pass