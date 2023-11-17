import os, uuid
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import src.utils.methods as umethods
from src.models.enums.azure import ContainerName

class AzureBlobHandler():
    
    def __init__(self, config):
        print("Azure Blob Storage Python quickstart sample")

        self.config = config

        # Quickstart code goes here
        self.account_url = self.config.get('Azure','account_url')
        self.default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        self.blob_service_client = BlobServiceClient(self.account_url, credential=self.default_credential)

        # Init Container Name 
        self.container_name = None

    def update_container_name(self, container_name : ContainerName):

        match container_name:
            case ContainerName.LiftInspection_Audio:
                self.container_name = self.config.get('Azure', 'container_li_audio')
            case ContainerName.LiftInspection_VideoFront:
                self.container_name = self.config.get('Azure', 'container_li_video_front')
            case ContainerName.LiftInspection_VideoRear:
                self.container_name = self.config.get('Azure', 'container_li_video_rear')
            case ContainerName.WaterLeakage_Thermal:
                self.container_name = self.config.get('Azure', 'container_wl_thermal_image')
            case ContainerName.WaterLeakage_VideoRear:
                self.container_name = self.config.get('Azure', 'container_wl_video_rear')
            case ContainerName.Surveillance_Audio:
                self.container_name = self.config.get('Azure', 'container_s_audio')
            case ContainerName.Surveillance_VideoFront:
                self.container_name = self.config.get('Azure', 'container_s_video_front')
            case ContainerName.Surveillance_VideoRear:
                self.container_name = self.config.get('Azure', 'container_s_video_rear')
            case ContainerName.Surveillance_Thermal:
                self.container_name = self.config.get('Azure', 'container_s_thermal_image')

    def upload_folder(self, upload_folder_path, folder_name):
        
        self.container_name = self.container_name + '/' +folder_name
        for file in Path(upload_folder_path).iterdir():
            self.upload_blobs(str(file))
        pass
    
    def upload_blobs(self, upload_file_path):
        
        file_path = Path(upload_file_path)

        # Create a file in the local data directory to upload and download
        local_file_name = file_path.name
        upload_file_path = str(file_path)

        # Create a blob client using the local file name as the name for the blob
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=local_file_name)

        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        # Upload the created file
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)
        
        pass

    def list_blobs(self):
        try:
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            print("\nListing blobs...")
            # List the blobs in the container
            blob_list = self.container_client.list_blobs()
            for blob in blob_list:
                print("\t" + blob.name)

        except Exception as ex:
            print('Exception:')
            print(ex)


if __name__ == '__main__':
    
    # # file_path = '/home/yf/SynologyDrive/Google Drive/Job/dev/w0405_agent/data/sounds/Records/20231115/996/recording_1700015268.066069.wav'

    # ## Method 1
    # # file_name = file_path.split('/')[-1]
    # # print(file_name)

    # ## Method 2

    # # file_path = Path('/home/yf/SynologyDrive/Google Drive/Job/dev/w0405_agent/data/sounds/Records/20231115/996/recording_1700015268.066069.wav')
    # file_path = Path('/home/yf/SynologyDrive/Google Drive/Job/dev/w0405_agent/src/handlers/20230906')
    # # print(file_path)
    # # print(file_path.name)
    # # print(file_path.suffix)
    # # print(file_path.stem)

    # config = umethods.load_config('../../conf/config.properties')
    # blob_handler = AzureBlobHandler(config)
    # # blob_handler.update_container_name(ContainerName.LiftInspection_Sound)
    # # blob_handler.list_blobs()

    # ## to azure container
    # blob_handler.update_container_name(ContainerName.WaterLeakage_Thermal)
    # blob_handler.upload_blobs(str(file_path))

    # ## to nwdb - sound/video_front/video_rear

    ### [thermal]
    ### Method 3 Upload folder with folder name
    folder_path = Path('/home/yf/SynologyDrive/Google Drive/Job/dev/w0405_agent/src/handlers/20230906')
    
    config = umethods.load_config('../../conf/config.properties')
    blob_handler = AzureBlobHandler(config)

    ## to azure container
    blob_handler.update_container_name(ContainerName.WaterLeakage_Thermal)
    blob_handler.upload_folder(str(folder_path), '0001')


    pass