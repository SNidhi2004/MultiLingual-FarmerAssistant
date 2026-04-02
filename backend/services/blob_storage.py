# from azure.storage.blob import BlobServiceClient
# import uuid
# from config import (
#     AZURE_BLOB_ACCOUNT,
#     AZURE_BLOB_KEY,
#     AZURE_BLOB_CONTAINER
# )

# def upload_image_to_blob(image_bytes: bytes) -> str:
#     """
#     Uploads image to Azure Blob Storage and returns public URL.
#     """
#     try:
#         blob_service = BlobServiceClient(
#             account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
#             credential=AZURE_BLOB_KEY
#         )
        
#         container_client = blob_service.get_container_client(AZURE_BLOB_CONTAINER)
        
#         from datetime import datetime
#         import uuid
#         timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#         unique_id = str(uuid.uuid4())[:8]
#         blob_name = f"audio/{user_id}_{timestamp}_{unique_id}.wav"
        
#         blob_client = container_client.get_blob_client(blob_name)
#         blob_client.upload_blob(audio_bytes, overwrite=True, content_type="audio/wav")
        
#         return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}"
        
#     except Exception as e:
#         print(f"Error uploading audio: {e}")
#         return None

# def upload_audio_to_blob(audio_bytes: bytes, user_id: str) -> str:
#     """
#     Uploads audio to Azure Blob Storage and returns public URL.
#     """
#     try:
#         from azure.storage.blob import BlobServiceClient
#         from config import AZURE_BLOB_ACCOUNT, AZURE_BLOB_KEY, AZURE_BLOB_CONTAINER
#         from datetime import datetime
#         import uuid
        
#         blob_service = BlobServiceClient(
#             account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
#             credential=AZURE_BLOB_KEY
#         )
        
#         container_client = blob_service.get_container_client(AZURE_BLOB_CONTAINER)
        
#         timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#         unique_id = str(uuid.uuid4())[:8]
#         blob_name = f"audio/{user_id}_{timestamp}_{unique_id}.wav"
        
#         blob_client = container_client.get_blob_client(blob_name)
#         blob_client.upload_blob(audio_bytes, overwrite=True, content_type="audio/wav")
        
#         return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}"
        
#     except Exception as e:
#         print(f"Error uploading audio: {e}")
#         return None

# from azure.storage.blob import BlobServiceClient
# import uuid
# from config import (
#     AZURE_BLOB_ACCOUNT,
#     AZURE_BLOB_KEY,
#     AZURE_BLOB_CONTAINER
# )

# def upload_image_to_blob(image_bytes: bytes) -> str:
#     """
#     Uploads image to Azure Blob Storage and returns public URL.
#     """
#     try:
#         blob_service = BlobServiceClient(
#             account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
#             credential=AZURE_BLOB_KEY
#         )
        
#         container_client = blob_service.get_container_client(AZURE_BLOB_CONTAINER)
        
#         # ✅ CORRECT: Use a simple UUID for image filename
#         blob_name = f"{uuid.uuid4()}.jpg"
        
#         blob_client = container_client.get_blob_client(blob_name)
#         blob_client.upload_blob(image_bytes, overwrite=True, content_type="image/jpeg")
        
#         return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}"
        
#     except Exception as e:
#         print(f"Error uploading image: {e}")
#         raise

# def upload_audio_to_blob(audio_bytes: bytes, user_id: str) -> str:
#     """
#     Uploads audio to Azure Blob Storage and returns public URL.
#     """
#     try:
#         from datetime import datetime
#         import uuid
        
#         blob_service = BlobServiceClient(
#             account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
#             credential=AZURE_BLOB_KEY
#         )
        
#         container_client = blob_service.get_container_client(AZURE_BLOB_CONTAINER)
        
#         timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#         unique_id = str(uuid.uuid4())[:8]
#         blob_name = f"audio/{user_id}_{timestamp}_{unique_id}.wav"
        
#         blob_client = container_client.get_blob_client(blob_name)
#         blob_client.upload_blob(audio_bytes, overwrite=True, content_type="audio/wav")
        
#         return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}"
        
#     except Exception as e:
#         print(f"Error uploading audio: {e}")
#         return None

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone
import uuid
from config import (
    AZURE_BLOB_ACCOUNT,
    AZURE_BLOB_KEY,
    AZURE_BLOB_CONTAINER
)

def upload_image_to_blob(image_bytes: bytes) -> str:
    try:
        blob_service = BlobServiceClient(
            account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
            credential=AZURE_BLOB_KEY
        )
        
        container_client = blob_service.get_container_client(AZURE_BLOB_CONTAINER)
        
        blob_name = f"{uuid.uuid4()}.jpg"
        
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(image_bytes, overwrite=True, content_type="image/jpeg")
        
        # Generate SAS token for 1 hour
        sas_token = generate_blob_sas(
            account_name=AZURE_BLOB_ACCOUNT,
            container_name=AZURE_BLOB_CONTAINER,
            blob_name=blob_name,
            account_key=AZURE_BLOB_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}?{sas_token}"
        
    except Exception as e:
        print(f"Error uploading image: {e}")
        raise

def upload_audio_to_blob(audio_bytes: bytes, user_id: str) -> str:
    try:
        from datetime import datetime, timezone
        
        blob_service = BlobServiceClient(
            account_url=f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net",
            credential=AZURE_BLOB_KEY
        )
        
        container_client = blob_service.get_container_client(AZURE_BLOB_CONTAINER)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        blob_name = f"audio/{user_id}_{timestamp}_{unique_id}.wav"
        
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(audio_bytes, overwrite=True, content_type="audio/wav")
        
        # Generate SAS token for 1 hour
        sas_token = generate_blob_sas(
            account_name=AZURE_BLOB_ACCOUNT,
            container_name=AZURE_BLOB_CONTAINER,
            blob_name=blob_name,
            account_key=AZURE_BLOB_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        return f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER}/{blob_name}?{sas_token}"
        
    except Exception as e:
        print(f"Error uploading audio: {e}")
        return None