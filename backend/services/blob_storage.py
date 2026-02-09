from azure.storage.blob import BlobServiceClient
import uuid
from config import (
    AZURE_BLOB_ACCOUNT,
    AZURE_BLOB_KEY,
    AZURE_BLOB_CONTAINER
)

def upload_image_to_blob(image_bytes: bytes) -> str:
    """
    Uploads image to Azure Blob Storage and returns public URL.
    """

    blob_service = BlobServiceClient(
        account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
        credential=AZURE_BLOB_KEY
    )

    container_client = blob_service.get_container_client(
        AZURE_BLOB_CONTAINER
    )

    blob_name = f"{uuid.uuid4()}.jpg"

    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(image_bytes, overwrite=True, content_type="image/jpeg")

    return (
        f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/"
        f"{AZURE_BLOB_CONTAINER}/{blob_name}"
    )
