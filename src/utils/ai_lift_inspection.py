import os
from pathlib import Path
from src.utils.tool_audio import AudioTool
from src.utils.tool_video import VideoTool
from src.utils.door_status_analyzer import DoorStatusAnalyzer
from src.utils.methods import convert_timestamp2date
from src.models.enums.nw import CameraPosition


class LiftInsectionAnalyser:
    def __init__(self,):
        self.temp_folder_dir = None
        self.preprocess_folder_dir = None
        
        self.raw_data_folder_dir = None
        self.raw_audio_dir = None
        self.raw_front_video_dir = None
        self.raw_rear_video_dir = None

        #logic
        self.mono_audio_dir = None

        #tools
        self.video_tool = VideoTool()
        self.audio_tool = AudioTool()
        self.dsa = DoorStatusAnalyzer()
        pass
    
    def set_raw_data_dir_path(self, audio_dir, front_video_dir, rear_video_dir):
        self.raw_audio_dir = audio_dir
        self.raw_front_video_dir = front_video_dir
        self.raw_rear_video_dir = rear_video_dir

        self.raw_audio_path = Path(audio_dir)
        self.raw_front_video_path = Path(front_video_dir)
        self.raw_rear_video_path = Path(rear_video_dir)        
        pass

    def set_temp_dir(self, temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        self.audio_tool.set_save_folder_dir(temp_dir)
        self.video_tool.set_save_folder_dir(temp_dir)

    # [Workflow]
    def get_raw_data_duration(self,):
        front_video_duration = self.video_tool.get_video_duration(self.raw_front_video_dir)
        rear_video_duration = self.video_tool.get_video_duration(self.raw_rear_video_dir)
        audio_duration = self.audio_tool.get_audio_duration(self.raw_audio_dir)
        print(f'[LiftInsectionTool] front_video_duration: {front_video_duration}')
        print(f'[LiftInsectionTool] rear_video_duration:  {rear_video_duration}')
        print(f'[LiftInsectionTool] audio_duration:       {audio_duration}')
        pass

    def preprocess_raw_audio(self):
        front_video_duration = self.video_tool.get_video_duration(self.raw_front_video_dir)
        front_video_start_timestamp = float(self.raw_front_video_path.stem.split('_')[-1])
        front_video_end_timestamp = front_video_start_timestamp + front_video_duration
        audio_end_timestamp = float(self.raw_audio_path.stem.split('_')[-1])
        audio_duration = self.audio_tool.get_audio_duration(self.raw_audio_dir)
        audio_start_timestamp = audio_end_timestamp - audio_duration

        front_video_start_date = convert_timestamp2date(front_video_start_timestamp)
        front_video_end_date = convert_timestamp2date(front_video_end_timestamp)
        audio_end_date = convert_timestamp2date(audio_end_timestamp)
        
        # Exception
        if(audio_duration < front_video_duration):
            print(f'[LiftInsectionTool] audio_duration is less than front_video_duration')
            print(f'[LiftInsectionTool] please check recording files...')
            # return False 
        if(front_video_end_timestamp >= audio_end_timestamp):
            print(f'[LiftInsectionTool] audio_end_timestamp is less than front_video_end_timestamp')
            print(f'[LiftInsectionTool] please check recording procedure...')
            # return False   
        
        audio_actual_end_timestamp = front_video_end_timestamp
        audio_actual_duration = front_video_duration
        trim_sec_from_end = audio_end_timestamp - front_video_end_timestamp

        trim_sec_from_start = front_video_start_timestamp - audio_start_timestamp

        trimmed_audio_dir = self.audio_tool.trim_audio(self.raw_audio_dir, start_sec=trim_sec_from_start, end_sec=trim_sec_from_start+front_video_duration)
        stereo_audio_dir = self.audio_tool.convert_to_stereo_audio(trimmed_audio_dir)
        foreground_file_dir, _ = self.audio_tool.separate_audio(stereo_audio_dir)
        self.mono_audio_dir = self.audio_tool.convert_to_mono_audio(foreground_file_dir) # mono_audio will be used for model training and inference
        mp3_audio_dir = self.audio_tool.convert_to_mp3(self.mono_audio_dir) # mp3 file will be uploaded to cloud

        # print(f'[LiftInsectionTool] front_video_duration: {front_video_duration}')
        # print(f'[LiftInsectionTool] front_video_start_tiemstamp:  {front_video_start_timestamp}')
        # print(f'[LiftInsectionTool] front_video_end_tiemstamp: {front_video_end_timestamp}') 
        # print(f'[LiftInsectionTool] audio_end_timestamp:       {audio_end_timestamp}')
        # print(f'[LiftInsectionTool] front_video_start_date:  {front_video_start_date}')    
        # print(f'[LiftInsectionTool] front_video_end_date:  {front_video_end_date}')       
        # print(f'[LiftInsectionTool] audio_end_date:  {audio_end_date}') 

        return self.mono_audio_dir

    def preprocess_raw_rear_video(self):
        predicted_video_dir, predicted_video_frames_dir, door_sliced_classes_dir = self.dsa.yolov8_detect_door_status()
        self.dsa.dsq.set_sliced_classes_dir(door_sliced_classes_dir)
        sliced_statuses = self.dsa.dsq.convert_classids2sliced_statuses()
        compact_statuses, compact_statuses_info = self.dsa.dsq.group_sliced_statuses(sliced_statuses)
        compact_door_statuses_info, door_compact_statuses_info_dir = self.dsa.dsq.analyze_door_sequence(compact_statuses, compact_statuses_info)
        # print(compact_door_statuses_info)
        return door_compact_statuses_info_dir
    
    def trim_audio_for_training(self):
        pass

if __name__ == '__main__':

    lfa = LiftInsectionAnalyser()

    # # EXAMPLE 1
    # lfa.set_raw_data_dir_path(audio_dir='data/lift-inspection/raw-data/20240318/001/recording_1709898801.1256263.wav',
    #                          front_video_dir='data/lift-inspection/raw-data/20240318/001/front_video_1709898640.302843.avi',
    #                          rear_video_dir='data/lift-inspection/raw-data/20240318/001/rear_video_1709898640.608474.avi')
    # lfa.set_temp_dir("data/lift-inspection/temp/20240318/001")

    # # [1] raw_audio -> temp_audio
    # mono_audio_dir = lfa.preprocess_raw_audio()

    # # [2] raw_rear_video -> compact_door_status
    # lfa.dsa.set_ckpt('../ai_module/door_status/ckpt/best.pt')
    # lfa.dsa.set_preprocess_folder_dir('data/lift-inspection/preprocess/'+ '20240318/001/'+"door-status/")
    # lfa.dsa.set_temp_folder_dir('data/lift-inspection/temp/'+ '20240318/001/')
    # lfa.dsa.set_source_video("data/lift-inspection/raw-data/20240318/001/rear_video_1709898640.608474.avi")
    # lfa.dsa.set_camera_position(CameraPosition.Rear)
    # door_compact_statuses_info_dir = lfa.preprocess_raw_rear_video()

    # # [3] compact_door_status + temp_audio => sliced_audio
    # # ...

    # EXAMPLE 2
    lfa.set_raw_data_dir_path(audio_dir='data/lift-inspection/raw-data/20240318/539/recording_1710761694.0095713.wav',
                             front_video_dir='data/lift-inspection/raw-data/20240318/539/front_video_1710761524.8510606.avi',
                             rear_video_dir='data/lift-inspection/raw-data/20240318/539/rear_video_1710761525.0664573.avi')
    lfa.set_temp_dir("data/lift-inspection/temp/20240318/539")

    # [1] raw_audio -> temp_audio
    mono_audio_dir = lfa.preprocess_raw_audio()

    # [2] raw_rear_video -> compact_door_status
    lfa.dsa.set_ckpt('../ai_module/door_status/ckpt/best.pt')
    lfa.dsa.set_preprocess_folder_dir('data/lift-inspection/preprocess/'+ '20240318/539/'+"door-status/")
    lfa.dsa.set_temp_folder_dir('data/lift-inspection/temp/'+ '20240318/539/')
    lfa.dsa.set_source_video("data/lift-inspection/raw-data/20240318/539/rear_video_1710761525.0664573.avi")
    lfa.dsa.set_camera_position(CameraPosition.Rear)
    door_compact_statuses_info_dir = lfa.preprocess_raw_rear_video()

    # [3] compact_door_status + temp_audio => sliced_audio
    # ...

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