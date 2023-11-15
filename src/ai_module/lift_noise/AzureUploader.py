import os, uuid
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

    def upload_blobs(self, file_path):
        
        # Create a file in the local data directory to upload and download
        local_file_name = str(uuid.uuid4()) + ".txt"
        upload_file_path = os.path.join(local_path, local_file_name)

        # Create a blob client using the local file name as the name for the blob
        blob_client = self.blob_service_client.get_blob_client(container='lift-sound', blob=local_file_name)

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
    
    blob_handler = AzureBlobStorageHandler()
    blob_handler.list_blobs()

    pass