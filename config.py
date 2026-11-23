import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "sahana-secure-cloud-gallery-secret-key-2026")
    
    # Storage Backend: 'local' (simulated S3 object storage) or 'aws' (Amazon S3)
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "sahana-secure-image-gallery")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "")
    
    # Local Storage Directory (Used when STORAGE_BACKEND is 'local')
    LOCAL_STORAGE_DIR = os.getenv("LOCAL_STORAGE_DIR", os.path.join(os.path.dirname(__file__), ".local_s3_storage"))
    
    # Upload Configurations
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"}
    
    # Server configuration
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
