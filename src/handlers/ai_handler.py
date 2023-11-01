# NW AI Agent - Rev01 -  2023.10.31
import math, time, threading
import src.models.robot as Robot
import src.utils.methods as umethods
# from src.models.schema.nw import Door, DoorRegion
# from src.top_module.analysis.region_handler import RegionHandler

from src.ai_module.lift_noise.AudioUtils import AudioUtils
from src.ai_module.lift_noise.AnomalyDetector import AnomalyDetector as AudioAnomalyDetector
from src.ai_module.lift_noise.AudioRecorder import Recorder as AudioRecorder

class AIAgent:
    def __init__(self, config, robot: Robot.Robot):
        self.robot = robot

        # params
        self.audio_record_path = ''
        self.audio_chunk_path = ''

        # for recording
        self.audio_recorder = AudioRecorder()

        # for preprocessing
        self.audio_utils = AudioUtils()
        
        # for inference
        self.audio_detector = AudioAnomalyDetector(self.audio_chunk_path)
        
    # Logic
    def update_audio_record_path(self, audio_record_path):
        '''
        Record/{current_date}/{mission_id}/
        '''
        self.audio_record_path = audio_record_path
        self.audio_recorder.update_save_path(self.audio_record_path)

        # self.video_record_path = video_record_path
        pass

    def update_audio_chunk_path(self, audio_chunk_path):
        '''
        Chunk/{current_date}/{mission_id}/
        '''
        self.audio_chunk_path = audio_chunk_path
        pass

    def start_recording(self):
        try:
            print(f'[ai_handler.start_recording] start recording...')
            self.audio_recorder.start_recording()
            return True
        except:
            return False

    def stop_recording(self):
        try:
            print(f'[ai_handler.stop_recording] stop recording, saving...')
            self.audio_recorder.save_record(self.audio_record_path)
            print(f'[ai_handler.stop_recording] finished.')
            return True
        except:
            return False

    def start_preporcessing(self):
        try:
            print(f'[ai_handler.start_preporcessing] start preporcessing...')
            self.audio_utils.split(self.audio_record_path, self.audio_chunk_path)
            print(f'[ai_handler.start_preporcessing] finished.')
            return True
        except:
            return False

    def start_analysing(self):
        try:
            print(f'[ai_handler.start_analysing] start analysing...')
            self.audio_detector.update_test_data_dir(config.get("RECORDING", 'chunk_path'))
            self.audio_detector.inference_classifier()
            self.audio_detector.inference_detector("ambient")
            self.audio_detector.inference_detector("vocal")
            self.audio_detector.inference_detector("door")
        except:
            return False


if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    robot = Robot.Robot(config,port_config)

    ai_handler = AIAgent(robot)
    
    