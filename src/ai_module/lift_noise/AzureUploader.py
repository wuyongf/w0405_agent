import os, uuid
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

class AzureBlobStorageHandler():
    
    def __init__(self):
        print("Azure Blob Storage Python quickstart sample")

        # Quickstart code goes here
        self.account_url = "https://nwistorage.blob.core.windows.net"
        self.default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        self.blob_service_client = BlobServiceClient(self.account_url, credential=self.default_credential)

        self.container_client = self.blob_service_client.get_container_client('image-ui')

    def update_container_name(self, container_name):
        self.container_name = container_name
    
    def upload_blobs(self, upload_file_path):
        
        file_path = Path(upload_file_path)

        # Create a file in the local data directory to upload and download
        local_file_name = file_path.name
        upload_file_path = str(file_path)

        # Create a blob client using the local file name as the name for the blob
        blob_client = self.blob_service_client.get_blob_client(container='lift-sound/wav', blob=local_file_name)

        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        # Upload the created file
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)
        
        pass

    def list_blobs(self):

        try:
            print("\nListing blobs...")
            # List the blobs in the container
            blob_list = self.container_client.list_blobs()
            for blob in blob_list:
                print("\t" + blob.name)

        except Exception as ex:
            print('Exception:')
            print(ex)


if __name__ == '__main__':
    
    file_path = '/home/yf/SynologyDrive/Google Drive/Job/dev/w0405_agent/data/sounds/Records/20231115/996/recording_1700015268.066069.wav'

    ## Method 1
    # file_name = file_path.split('/')[-1]
    # print(file_name)

    ## Method 2
    

    file_path = Path('/home/yf/SynologyDrive/Google Drive/Job/dev/w0405_agent/data/sounds/Records/20231115/996/recording_1700015268.066069.wav')
    print(file_path)

    print(file_path.name)
    print(file_path.suffix)
    print(file_path.stem)

    blob_handler = AzureBlobStorageHandler()
    # blob_handler.list_blobs()
    blob_handler.upload_blobs(str(file_path))

    pass