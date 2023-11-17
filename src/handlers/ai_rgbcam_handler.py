# NW Audio Agent - Rev01 -  2023.10.31
from pathlib import Path
import shutil
import math, time, threading, os
# import src.models.robot as Robot
import src.utils.methods as umethods
# from src.ai_module.lift_noise.AudioUtils import AudioUtils
# from src.ai_module.lift_noise.AnomalyDetector import AnomalyDetector as AudioAnomalyDetector
from src.top_module.module.microphone import Recorder as AudioRecorder
from src.top_module.module.rgbcam import RGBCamRecorder
from src.handlers.azure_blob_handler import AzureBlobHandler
from src.models.enums.nw import InspectionType
from src.models.enums.azure import ContainerName
from src.models.db_robot import robotDBHandler
import src.models.enums.nw as NWEnums

class RGBCamAgent:
    def __init__(self, config, device_index):
        # self.robot = robot
        self.config = config
        
        # params
        self.video_record_path = ''

        # for recording
        self.recorder = RGBCamRecorder(device_index)
        # self.rgbcam_recorder_rear = RGBCamRecorder(device_index=2)
    
    # Logic - Level 2
    def construct_paths(self, mission_id, inspection_type: InspectionType, camera_position: NWEnums.CameraPosition):
        '''
        create 3 paths:
        1. audio_record_path
        2. audio_chunk_path
        3. audio_infer_result_path
        '''
        match inspection_type:
            case InspectionType.LiftInspection:
                if camera_position == NWEnums.CameraPosition.Front:
                    self.container_name = self.config.get('Azure', 'container_li_video_front')
                if camera_position == NWEnums.CameraPosition.Rear:
                    self.container_name = self.config.get('Azure', 'container_li_video_rear')

        self.relative_data_dir = self.config.get('Data', 'data_dir')
        self.relative_result_dir = self.config.get('Data', 'result_dir')
        self.current_date = umethods.get_current_date()
        self.mission_id = str(mission_id)

        self.data_dir = Path(str(Path().cwd() / self.relative_data_dir / self.container_name))
        self.data_dir.mkdir(exist_ok=True, parents=True)

        self.result_dir = Path(str(Path().cwd() / self.relative_result_dir / self.container_name))
        self.result_dir.mkdir(exist_ok=True, parents=True)

        ### construct the folder path
        self.video_record_path = self.data_dir / self.current_date / self.mission_id
        # self.audio_infer_result_path = self.result_dir /  self.current_date / self.mission_id

        ### create folders
        self.video_record_path.mkdir(exist_ok=True, parents=True)
        # self.audio_infer_result_path.mkdir(exist_ok=True, parents=True)

        ### clear the folder first
        # shutil.rmtree(self.audio_record_path)
        # shutil.rmtree(self.audio_chunk_path)
        # shutil.rmtree(self.audio_infer_result_path)

        # # create folders
        # self.audio_record_path.mkdir(exist_ok=True, parents=True)
        # self.audio_chunk_path.mkdir(exist_ok=True, parents=True)
        # self.audio_infer_result_path.mkdir(exist_ok=True, parents=True)        

        ## notify recorder the save path
        self.recorder.update_save_path(output_dir=self.video_record_path)
        # self.audio_recorder.update_save_path(self.video_record_path)

        return str(self.video_record_path)

    def start_recording(self):
        try:
            print(f'[ai_rgbcam_handler.start_recording] start recording...')
            self.recorder.capture_and_save_video()
            return True
        except:
            return False

    def stop_and_save_recording(self):
        '''
        return wav file path
        '''
        try:
            print(f'[ai_rgbcam_handler.stop_and_save_recording] stop recording, saving...')
            video_file_name = self.recorder.stop_and_save_record()
            print(f'[ai_rgbcam_handler.stop_and_save_recording] finished.')

            return video_file_name
        except:
            return False

    def start_slicing(self):
        pass

    def start_analysing(self):
        pass

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    video_handler = RGBCamAgent(config, device_index=2)

    video_handler.construct_paths(mission_id=990, inspection_type=InspectionType.LiftInspection, camera_position=NWEnums.CameraPosition.Front)

    video_handler.start_recording()

    time.sleep(10)

    video_file_path = video_handler.stop_and_save_recording()
    
    ###  Video - Notify User

    ###  Video - upload to cloud (1. Azure Container) 
    blob_handler = AzureBlobHandler(config)
    blob_handler.update_container_name(ContainerName.LiftInspection_VideoFront)
    blob_handler.upload_blobs(video_file_path)

    mp4_file_name = Path(video_file_path).name
    print(str(mp4_file_name))

    # Video - upload to cloud (2. NWDB)
    nwdb = robotDBHandler(config)
    nwdb.insert_new_video_id(NWEnums.CameraPosition.Front, robot_id=1, mission_id=2, video_file_name=mp4_file_name)
    video_id = nwdb.get_latest_video_id(NWEnums.CameraPosition.Front)
    # nwdb.insert_new_audio_analysis(audio_id=video_id, formatted_output_list=formatted_output, audio_type=NWEnums.AudioType.Door)

    # - notify user
    
