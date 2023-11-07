# NW AI Agent - Rev01 -  2023.10.31
import math, time, threading, os
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
        self.audio_infer_result_path = ''

        # for recording
        self.audio_recorder = AudioRecorder()

        # for preprocessing
        self.audio_utils = AudioUtils()
        
        # for inference
        self.audio_detector = AudioAnomalyDetector(config)
        
    # Logic
    def update_audio_record_path(self, audio_record_path):
        '''
        Record/{current_date}/{mission_id}/
        '''
        self.audio_record_path = audio_record_path
        self.audio_recorder.update_save_path(self.audio_record_path)
        if not os.path.exists(self.audio_record_path): os.makedirs(self.audio_record_path)

        # self.video_record_path = video_record_path
        pass

    def update_audio_chunk_path(self, audio_chunk_path):
        '''
        Chunk/{current_date}/{mission_id}/
        '''
        self.audio_chunk_path = audio_chunk_path
        if not os.path.exists(self.audio_chunk_path): os.makedirs(self.audio_chunk_path)
        pass

    def update_audio_infer_result_path(self, audio_infer_result_path):
        self.audio_infer_result_path = audio_infer_result_path
        if not os.path.exists(self.audio_infer_result_path): os.makedirs(self.audio_infer_result_path)
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
            self.audio_recorder.save_record()
            print(f'[ai_handler.stop_recording] finished.')
            return True
        except:
            return False

    def start_slicing(self):
        try:
            print(f'[ai_handler.start_slicing] start slicing...')
            for file_name in os.listdir(self.audio_record_path):
                file_path = os.path.join(self.audio_record_path, file_name)
                self.audio_utils.split(file_path, file_name, self.audio_chunk_path)
            print(f'[ai_handler.start_slicing] finished.')
            return True
        except:
            return False

    def start_analysing(self):
        try:
            print(f'[ai_handler.start_analysing] start analysing...')
            self.audio_detector.update_test_data_dir(self.audio_chunk_path)
            self.audio_detector.update_infer_result_path(self.audio_infer_result_path)
            self.audio_detector.inference_classifier()
            self.audio_detector.inference_detector("ambient")
            self.audio_detector.inference_detector("vocal")
            self.audio_detector.inference_detector("door")
        except:
            return False
        
    def start_merging(self, vocal):

        overlay_sec = self.audio_utils.overlap_sec

        # Sort the clips by slice number
        vocal.sort(key=lambda clip: int(clip.split("_")[2]))

        merged_clips = []
        current_clip = vocal[0]
        current_slice_number = int(current_clip.split("_")[2])
        current_start_time = int(current_clip.split("_")[3])
        current_end_time = int(current_clip.split("_")[4].split(".")[0])

        for clip in vocal[1:]:
            clip_slice_number = int(current_clip.split("_")[2])
            clip_start = int(current_clip.split("_")[3])
            clip_end = int(current_clip.split("_")[4].split(".")[0])

            if clip_slice_number == current_slice_number + 1 and clip_start == current_end_time - overlay_sec*1000:
                # Extend the current clip
                current_end_time = clip_end
            else:
                # Add the current clip to the merged list and start a new one
                merged_clips.append((current_start_time, current_end_time))
                current_clip = clip
                current_start_time = clip_start
                current_end_time = clip_end

        # Add the last clip to the merged list
        merged_clips.append((current_start_time, current_end_time))

        # Format the merged clips as "start_time_end_time"
        formatted_merged_clips = [f"{start}_{end}" for start, end in merged_clips]

        return formatted_merged_clips




if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    port_config = umethods.load_config('../../conf/port_config.properties')
    skill_config_path = '../models/conf/rm_skill.properties'
    ai_config = umethods.load_config('../ai_module/lift_noise/cfg/config.properties')
    robot = Robot.Robot(config,port_config,skill_config_path)
    ai_handler = AIAgent(ai_config,robot)

    # Init
    ai_handler.update_audio_record_path('/home/nw/Documents/GitHub/w0405_agent/data/sounds/Records/20231107/996')
    ai_handler.update_audio_chunk_path('/home/nw/Documents/GitHub/w0405_agent/data/sounds/Chunk/20231107/996')
    ai_handler.update_audio_infer_result_path('/home/nw/Documents/GitHub/w0405_agent/results/sounds/Chunk/20231107/996')

    # # Sound - Record
    # ai_handler.start_recording()
    # time.sleep(1)
    # ai_handler.stop_recording()

    # # Sound - Slicing
    # ai_handler.start_slicing()

    # Sound - Analyse
    # ai_handler.start_analysing()

    vocal = [
        "recording_1699332347.8895252_5_16000_21000.wav",
        "recording_1699332347.8895252_8_28000_33000.wav",
        "recording_1699332347.8895252_15_56000_60163.wav",
        "recording_1699332347.8895252_4_12000_17000.wav",
        "recording_1699332347.8895252_14_52000_57000.wav",
        "recording_1699332347.8895252_3_8000_13000.wav",
        "recording_1699332347.8895252_1_0_5000.wav",
        "recording_1699332347.8895252_13_48000_53000.wav",
        "recording_1699332347.8895252_6_20000_25000.wav"
    ]

    # 1  3456 8 131415

    merged_clips =  ai_handler.start_merging(vocal)
    # print("Merged Clips:", merged_clips)




    print("Merged Clips:", merged_clips)

    # Find how many clips can be merged
    print(f"Number of Merged Clips: {len(merged_clips)}")

    # Point out the start and end times of each merged clip
    for idx, clip in enumerate(merged_clips):
        start, end = clip.split("_")
        print(f"Clip {idx + 1}: Start Time {start}, End Time {end}")

    

    
    

    