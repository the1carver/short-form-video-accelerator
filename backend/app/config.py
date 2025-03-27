from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-west-2")
    tiktok_api_key: str = os.getenv("TIKTOK_API_KEY", "")
    descript_api_key: str = os.getenv("DESCRIPT_API_KEY", "")
    openai_whisper_api_key: str = os.getenv("OPENAI_WHISPER_API_KEY", "")
    stripe_api_key: str = os.getenv("STRIPE_API_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Application Settings
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_google_video_intelligence: bool = os.getenv("ENABLE_GOOGLE_VIDEO_INTELLIGENCE", "False").lower() == "true"
    
    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite://")
    firebase_credentials: str = os.getenv("FIREBASE_CREDENTIALS", "") or os.path.join(os.path.dirname(__file__), "credentials/google_credentials.json")
    
    # AWS S3 Settings
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "digital-frontier-assets")
    s3_region: str = os.getenv("S3_REGION", "us-west-2")
    
    # AWS Lambda Settings
    lambda_function_name: str = os.getenv("LAMBDA_FUNCTION_NAME", "video-processing")
    
    # Video Processing Settings
    max_video_size_mb: int = 500
    supported_video_formats: list[str] = ["mp4", "mov", "avi", "mkv"]
    output_video_format: str = "mp4"
    
    # TikTok Settings
    tiktok_video_max_length_seconds: int = 60
    tiktok_aspect_ratios: list[str] = ["9:16", "1:1", "16:9"]
    default_tiktok_aspect_ratio: str = "9:16"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings object
settings = Settings()
