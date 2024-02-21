# NW AI Agent - Rev01 -  2023.10.31
from pathlib import Path
import shutil
import math, time, threading, os
import json
# import src.models.robot as Robot
import src.utils.methods as umethods
from src.ai_module.lift_noise.AudioUtils import AudioUtils
from src.ai_module.lift_noise.AnomalyDetector import AnomalyDetector as AudioAnomalyDetector
from src.top_module.module.microphone import Recorder as AudioRecorder
from src.handlers.azure_blob_handler import AzureBlobHandler
from src.models.enums.nw import InspectionType
from src.models.enums.azure import ContainerName
from src.models.db_robot import robotDBHandler
import src.models.enums.nw as NWEnums
# DEBUG
from src.top_module.module.rgbcam import RGBCamRecorder

class AudioAgent:
    def __init__(self, config, ai_config):
        # self.robot = robot
        self.config = config
        
        # params
        self.audio_record_path = ''
        self.audio_chunk_path = ''
        self.audio_infer_result_path = ''

        # for recording
        self.audio_recorder = AudioRecorder()

        ### DEBUG
        # rgbcam =  RGBCamRecorder(device_index=0)
        # rgbcam.update_cap_save_path('test')
        # rgbcam.cap_open_cam()
        # rgbcam.cap_rgb_img('test24.jpg')

        # for preprocessing
        self.audio_utils = AudioUtils()
        
        # for inference
        self.audio_detector = AudioAnomalyDetector(ai_config)
    
    # Logic - Level 2
    def construct_folder_paths(self, mission_id, inspection_type: InspectionType):
        '''
        create 3 paths:
        1. audio_record_path
        2. audio_chunk_path
        3. audio_infer_result_path
        '''
        match inspection_type:
            case InspectionType.LiftInspection:
                self.container_name = self.config.get('Azure', 'container_li_audio')

        self.relative_data_dir = self.config.get('Data', 'data_dir')
        self.relative_result_dir = self.config.get('Data', 'result_dir')
        self.current_date = umethods.get_current_date()
        self.mission_id = str(mission_id)

        self.data_dir = Path(str(Path().cwd() / self.relative_data_dir / self.container_name))
        self.data_dir.mkdir(exist_ok=True, parents=True)

        self.result_dir = Path(str(Path().cwd() / self.relative_result_dir / self.container_name))
        self.result_dir.mkdir(exist_ok=True, parents=True)

        # construct the folder path
        self.audio_record_path = self.data_dir / 'Records' / self.current_date / self.mission_id
        self.audio_chunk_path  = self.data_dir / 'Chunk' / self.current_date / self.mission_id
        self.audio_infer_result_path = self.result_dir /  self.current_date / self.mission_id

        # create folders
        self.audio_record_path.mkdir(exist_ok=True, parents=True)
        self.audio_chunk_path.mkdir(exist_ok=True, parents=True)
        self.audio_infer_result_path.mkdir(exist_ok=True, parents=True)

        # # clear the folder first
        # shutil.rmtree(self.audio_record_path)
        # shutil.rmtree(self.audio_chunk_path)
        # shutil.rmtree(self.audio_infer_result_path)

        # # create folders
        # self.audio_record_path.mkdir(exist_ok=True, parents=True)
        # self.audio_chunk_path.mkdir(exist_ok=True, parents=True)
        # self.audio_infer_result_path.mkdir(exist_ok=True, parents=True)        

        ## notify recorder the save path
        self.audio_recorder.update_save_path(self.audio_record_path)

        return [str(self.audio_record_path), str(self.audio_chunk_path), str(self.audio_infer_result_path)]

    # # Logic - Level 1
    # def update_record_path(self, audio_record_path):
    #     '''
    #     Record/{current_date}/{mission_id}/
    #     '''
    #     self.audio_record_path = audio_record_path
    #     self.audio_recorder.update_save_path(self.audio_record_path)
    #     if not os.path.exists(self.audio_record_path): os.makedirs(self.audio_record_path)

    #     return(str(Path(self.audio_record_path).absolute()))

    # def update_chunk_path(self, audio_chunk_path):
    #     '''
    #     Chunk/{current_date}/{mission_id}/
    #     '''
    #     self.audio_chunk_path = audio_chunk_path
    #     if not os.path.exists(self.audio_chunk_path): os.makedirs(self.audio_chunk_path)
        
    #     return(str(Path(self.audio_chunk_path).absolute()))

    # def update_infer_result_path(self, audio_infer_result_path):
    #     self.audio_infer_result_path = audio_infer_result_path
    #     if not os.path.exists(self.audio_infer_result_path): os.makedirs(self.audio_infer_result_path)
    #     return(str(Path(self.audio_infer_result_path).absolute()))

    def get_abnormal_sound(self, item):

        print(f'item: {item}')

        # Assuming your JSON file is named 'your_file.json'
        result_path = str(self.audio_infer_result_path)

        print(f'result_path: {result_path}')
        file_name = item + '.json'
        file_path = os.path.join(result_path, file_name)

        print(file_path)

        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Get the content of 'abnormal'
        abnormal_content = data['abnormal']

        # print(abnormal_content)
        return abnormal_content
    
    def group_abnormal_sound(self, item):
        try:
            sound_json = self.get_abnormal_sound(item)
            print(f'sound_json: {sound_json}')
            if(len(sound_json) != 0):
                self.audio_utils.group_init(sound_json)
                print(f'xx1')
                grouped_intervals = self.audio_utils.group_overlapping_intervals()
                print(f'xx2')
                formatted_output = self.audio_utils.format_grouped_intervals(grouped_intervals)
                print(f'xx3')
                print(formatted_output)
                return formatted_output
            else:
                print(f'[group_abnormal_sound][{item}] Did not find any abnormal sound!')
                return None
        except:
            print(f'xx4')
            return None


    def start_recording(self):
        try:
            print(f'[ai_audio_handler.start_recording] start recording...')
            self.audio_recorder.start_recording()
            return True
        except:
            return False

    def stop_and_save_recording(self):
        '''
        return wav file path
        '''
        try:
            print(f'[ai_audio_handler.stop_and_save_recording] stop recording, saving...')
            wav_file_name = self.audio_recorder.stop_and_save_record()
            print(f'[ai_audio_handler.stop_and_save_recording] finished.')

            return wav_file_name
        except:
            return False

    def start_slicing(self):
        try:
            print(f'[ai_audio_handler.start_slicing] start slicing...')
            for file_name in os.listdir(str(self.audio_record_path)):
                file_path = os.path.join(str(self.audio_record_path), file_name)
                self.audio_utils.split(file_path, file_name, str(self.audio_chunk_path))
            print(f'[ai_audio_handler.start_slicing] finished.')
            return True
        except:
            return False

    def start_analysing(self):
        try:
            print(f'[ai_audio_handler.start_analysing] start analysing...')
            self.audio_detector.update_test_data_dir(str(self.audio_chunk_path))
            self.audio_detector.update_infer_result_path(str(self.audio_infer_result_path))
            self.audio_detector.inference_classifier()
            self.audio_detector.inference_detector("ambient")
            self.audio_detector.inference_detector("vocal")
            self.audio_detector.inference_detector("door")
        except:
            return False

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    # port_config = umethods.load_config('../../conf/port_config.properties')
    # skill_config_path = '../models/conf/rm_skill.properties'
    # robot = Robot.Robot(config,port_config,skill_config_path)
    ai_config = umethods.load_config('../ai_module/lift_noise/cfg/config.properties')
    audio_handler = AudioAgent(config, ai_config)

    audio_handler.construct_folder_paths(mission_id=991, inspection_type=InspectionType.LiftInspection)

    # Init
    # ai_handler.update_audio_record_path('/home/nw/Documents/GitHub/w0405_agent/data/sounds/Records/20231107/996')
    # ai_handler.update_audio_chunk_path('/home/nw/Documents/GitHub/w0405_agent/data/sounds/Chunk/20231107/996')
    # ai_handler.update_audio_infer_result_path('/home/nw/Documents/GitHub/w0405_agent/results/sounds/Chunk/20231107/996')
    
    # audio_record_path = audio_handler.update_record_path('../../data/lift-inspection/audio/Records/20231116/996')
    # audio_chunk_path = audio_handler.update_chunk_path('../../data/lift-inspection/audio/Chunk/20231116/996')
    # audio_infer_result_path = audio_handler.update_infer_result_path('../../results/lift-inspection/audio/Chunk/20231116/996')

    # Sound - Record
    audio_handler.start_recording()
    time.sleep(60)
    wav_file_name = audio_handler.stop_and_save_recording()
    print(wav_file_name)

    # Sound - Slicing
    audio_handler.start_slicing()

    # Sound - Analyse
    audio_handler.start_analysing()

    # Sound - Group Abnormal Sound
    formatted_output = audio_handler.group_abnormal_sound('vocal')
    # sound_json = audio_handler.get_abnormal_sound('vocal')
    # print(sound_json)
    # if(len(sound_json) != 0):
    #     processor = audio_handler.audio_utils.group_init(sound_json)
    #     grouped_intervals = audio_handler.audio_utils.group_overlapping_intervals()
    #     formatted_output = audio_handler.audio_utils.format_grouped_intervals(grouped_intervals)
    #     print(formatted_output)
    # else:
    #     print(f'Did not find any abnormal sound!')
    
    ##  Sound - Notify User
    ### convert to mp3 
    mp3_file_path  = audio_handler.audio_utils.convert_to_mp3('/home/yf/SynologyDrive/Google Drive/Job/dev/w0405_agent/data/lift-inspection/audio/Records/20231116/991/recording_1697180728.747398.wav')

    # # Sound - upload to cloud (1. Azure Container) 
    blob_handler = AzureBlobHandler(config)
    blob_handler.update_container_name(ContainerName.LiftInspection_Audio)
    blob_handler.upload_blobs(mp3_file_path)

    mp3_file_name = Path(mp3_file_path).name
    print(str(mp3_file_name))

    # Sound - upload to cloud (2. NWDB)
    nwdb = robotDBHandler(config)
    # nwdb.insert_new_audio_id(robot_id=1, mission_id=1, audio_file_name=mp3_file_name, is_abnormal=True)
    audio_id = nwdb.get_latest_audio_id()
    nwdb.insert_new_audio_analysis(audio_id=audio_id, formatted_output_list=formatted_output, audio_type=NWEnums.AudioType.Door)

    # - notify user
    
