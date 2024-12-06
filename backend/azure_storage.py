import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import uuid

# Azure Blob Storage configurations
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = 'audiofiles'  

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def upload_audio_to_blob(audio_stream, filename=None):
    """
    Uploads an audio stream to Azure Blob Storage.
    Returns the filename used in the blob storage.
    """
    if not filename:
        filename = f"{uuid.uuid4()}.mp3"

    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(audio_stream, overwrite=True)

    return filename

def generate_blob_sas_url(filename, expiry_hours=1):
    """
    Generates a SAS URL for the uploaded audio file.
    """
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=CONTAINER_NAME,
        blob_name=filename,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
    )

    audio_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{filename}?{sas_token}"
    return audio_url
