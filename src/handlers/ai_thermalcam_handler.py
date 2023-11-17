# NW Audio Agent - Rev01 -  2023.10.31
from pathlib import Path
import shutil
import math, time, threading, os
import src.utils.methods as umethods

from src.top_module.module.thermalcam import ThermalCam
from src.handlers.azure_blob_handler import AzureBlobHandler
from src.models.enums.nw import InspectionType
from src.models.enums.azure import ContainerName
from src.models.db_robot import robotDBHandler
import src.models.enums.nw as NWEnums

class ThermalCamAgent:
    def __init__(self, config):
        # self.robot = robot
        self.config = config
        
        # params
        self.image_record_path = ''

        # for recording
        self.recorder = ThermalCam(debug=False)
    
    # Logic - Level 2
    def construct_paths(self, mission_id, inspection_type: InspectionType):
        '''
        create 3 paths:
        1. audio_record_path
        2. audio_chunk_path
        3. audio_infer_result_path
        '''
        match inspection_type:
            case InspectionType.WaterLeakage:
                self.container_name = self.config.get('Azure', 'container_wl_thermal_image')

        self.relative_data_dir = self.config.get('Data', 'data_dir')
        self.relative_result_dir = self.config.get('Data', 'result_dir')
        self.current_date = umethods.get_current_date()
        self.mission_id = str(mission_id)

        self.data_dir = Path(str(Path().cwd() / self.relative_data_dir / self.container_name))
        self.data_dir.mkdir(exist_ok=True, parents=True)

        self.result_dir = Path(str(Path().cwd() / self.relative_result_dir / self.container_name))
        self.result_dir.mkdir(exist_ok=True, parents=True)

        ### construct the folder path
        self.image_record_path = self.data_dir / self.current_date / self.mission_id
        # self.audio_infer_result_path = self.result_dir /  self.current_date / self.mission_id

        ### create folders
        self.image_record_path.mkdir(exist_ok=True, parents=True)
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
        self.recorder.set_save_folder(self.image_record_path)
        # self.audio_recorder.update_save_path(self.video_record_path)

        return str(self.image_record_path)

    def start_capturing(self):
        try:
            print(f'[ai_thermalcam_handler.start_capturing] start capturing...')
            interval = 1
            threading.Thread(target=self.recorder.thread_start_capturing, args=(interval, )).start()
            return True
        except:
            return False

    def stop_capturing(self):
        '''
        return wav file path
        '''
        try:
            print(f'[ai_thermalcam_handler.stop_capturing] stop capturing, saving...')
            save_folder = self.recorder.stop_capturing()
            print(f'[ai_thermalcam_handler.stop_capturing] finished.')

            return save_folder
        except:
            return False

    def start_analysing(self):
        pass

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    themalcam_handler = ThermalCamAgent(config)

    themalcam_handler.construct_paths(mission_id=989, inspection_type=InspectionType.WaterLeakage)

    themalcam_handler.start_capturing()

    time.sleep(10)

    image_folder_path = themalcam_handler.stop_capturing()
    
    ###  Video - Notify User

    ###  Video - upload to cloud (1. Azure Container) 
    blob_handler = AzureBlobHandler(config)
    blob_handler.update_container_name(ContainerName.WaterLeakage_Thermal)
    folder_name = image_folder_path.split('/')[-1]
    blob_handler.upload_folder(image_folder_path, folder_name)

    # mp4_file_name = Path(video_file_path).name
    # print(str(mp4_file_name))

    # Video - upload to cloud (2. NWDB)
    nwdb = robotDBHandler(config)
    nwdb.insert_new_thermal_id(robot_id=1, mission_id=3, image_folder_name=folder_name)
    video_id = nwdb.get_latest_thermal_id(NWEnums.CameraPosition.Front)
    # nwdb.insert_new_audio_analysis(audio_id=video_id, formatted_output_list=formatted_output, audio_type=NWEnums.AudioType.Door)

    # - notify user
    
