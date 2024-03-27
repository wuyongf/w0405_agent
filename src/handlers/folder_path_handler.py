from pathlib import Path
import src.utils.methods as umethods
import src.models.enums.nw as NWEnums
from src.models.enums.nw import InspectionType, InspectionDataType

class FolderPathHandler:
    def __init__(self, config):
        self.config = config

        # path
        self.output_folder_path = None
        
    def construct_paths(self, mission_id, inspection_type: InspectionType, data_type: InspectionDataType):
        match inspection_type:
            case InspectionType.LiftInspection:
                match data_type:
                    case InspectionDataType.Audio:
                        self.container_name = self.config.get('Azure', 'container_li_audio')
                    case InspectionDataType.VideoFront:
                        self.container_name = self.config.get('Azure', 'container_li_video_front')
                    case InspectionDataType.VideoRear:
                        self.container_name = self.config.get('Azure', 'container_li_video_rear')
                    case InspectionDataType.Preprocess:
                        self.container_name = self.config.get('Azure', 'container_li_preprocess')
                    case InspectionDataType.Temp:
                        self.container_name = self.config.get('Azure', 'container_li_temp')
            case InspectionType.WaterLeakage:
                match data_type:
                    case InspectionDataType.RGBImage:
                        self.container_name = self.config.get('Azure', 'container_wl_rgb_image')
                    case InspectionDataType.ThermalImage:
                        self.container_name = self.config.get('Azure', 'container_wl_thermal_image')
                    case InspectionDataType.ThermalImageResult:
                        self.container_name = self.config.get('Azure', 'container_wl_thermal_image_result')
                    case InspectionDataType.WaterLeak_VideoRear:
                        self.container_name = self.config.get('Azure', 'container_wl_video_rear')


        self.relative_data_dir = self.config.get('Data', 'data_dir')
        self.relative_result_dir = self.config.get('Data', 'result_dir')
        self.current_date = umethods.get_current_date()
        self.mission_id = str(f'{mission_id:03d}')

        self.container_folder_path = Path(str(Path().cwd() / self.relative_data_dir / self.container_name))
        self.container_folder_path.mkdir(exist_ok=True, parents=True)

        self.result_container_folder_path = Path(str(Path().cwd() / self.relative_result_dir / self.container_name))
        self.result_container_folder_path.mkdir(exist_ok=True, parents=True)

        ### construct the folder path
        self.output_folder_path = self.container_folder_path / self.current_date / self.mission_id
        # {container_name}/{current_date}/{mission_id}
        # e.g. lift-inspection/video-front/20220222/001

        ### create folders
        self.output_folder_path.mkdir(exist_ok=True, parents=True)

        return str(self.output_folder_path)

if __name__ == '__main__':
    config = umethods.load_config('../../conf/config.properties')
    fph = FolderPathHandler(config)

    mission_id = 1
    inspection_type = InspectionType.LiftInspection
    data_type  = InspectionDataType.Preprocess
    res = fph.construct_paths(mission_id,inspection_type,data_type)
    print(res)
    pass