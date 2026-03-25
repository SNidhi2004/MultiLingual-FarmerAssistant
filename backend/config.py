import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    JWT_SECRET = "dev-secret-key-change-in-production" 

# Azure Speech
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Azure Translator
AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")

# Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

AZURE_BLOB_ACCOUNT = os.getenv("AZURE_BLOB_ACCOUNT")
AZURE_BLOB_KEY = os.getenv("AZURE_BLOB_KEY")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER")

# System limits
MAX_IMAGES_PER_SESSION = 3
MAX_QA_PER_IMAGE = 5
