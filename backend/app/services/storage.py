import logging
import boto3
import os
from typing import Optional
from ..config import settings

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.s3_client = None
        self.s3_bucket_name = settings.s3_bucket_name
        self.s3_region = settings.aws_region
        self.s3_endpoint_url = os.getenv("AWS_ENDPOINT_URL_S3")
        self.initialize_s3()
    
    def initialize_s3(self):
        """Initialize AWS S3 client"""
        try:
            if self.s3_endpoint_url and settings.aws_access_key_id and settings.aws_secret_access_key:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=self.s3_endpoint_url,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key
                )
                logger.info("Fly.io Tigris storage client initialized successfully")
            elif settings.aws_access_key_id and settings.aws_secret_access_key:
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.s3_region,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key
                )
                logger.info("AWS S3 client initialized successfully")
            else:
                logger.warning("AWS credentials not provided, S3 operations will be simulated")
        except Exception as e:
            logger.error(f"Error initializing S3 client: {str(e)}")
            # Continue without S3 for development
    
    async def upload_file(self, file_path: str, key: str, content_type: Optional[str] = None) -> str:
        """
        Upload a file to S3 bucket.
        
        Args:
            file_path: Path to the file to upload
            key: S3 key (path within bucket)
            content_type: MIME type of the file (optional)
            
        Returns:
            URL of the uploaded file
        """
        if not self.s3_client:
            logger.info(f"Simulating S3 upload (no AWS credentials): {key}")
            return f"https://example.com/{key}"
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_file(
                file_path,
                self.s3_bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            url = f"https://{self.s3_bucket_name}.s3.{self.s3_region}.amazonaws.com/{key}"
            logger.info(f"Uploaded file to S3: {url}")
            return url
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            # Fallback to a simulated URL
            return f"https://example.com/{key}"
    
    async def download_file(self, key: str, destination_path: str) -> bool:
        """
        Download a file from S3 bucket.
        
        Args:
            key: S3 key (path within bucket)
            destination_path: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            logger.info(f"Simulating S3 download (no AWS credentials): {key}")
            return False
        
        try:
            self.s3_client.download_file(
                self.s3_bucket_name,
                key,
                destination_path
            )
            
            logger.info(f"Downloaded file from S3: {key} to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return False
    
    async def delete_file(self, key: str) -> bool:
        """
        Delete a file from S3 bucket.
        
        Args:
            key: S3 key (path within bucket)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            logger.info(f"Simulating S3 delete (no AWS credentials): {key}")
            return True
        
        try:
            self.s3_client.delete_object(
                Bucket=self.s3_bucket_name,
                Key=key
            )
            
            logger.info(f"Deleted file from S3: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            return False
    
    async def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for an S3 object.
        
        Args:
            key: S3 key (path within bucket)
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.s3_client:
            logger.info(f"Simulating S3 presigned URL (no AWS credentials): {key}")
            return f"https://example.com/{key}?presigned=true"
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.s3_bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for S3 object: {key}")
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None
    
    async def list_files(self, prefix: str = "") -> list:
        """
        List files in S3 bucket with a given prefix.
        
        Args:
            prefix: S3 key prefix to filter by
            
        Returns:
            List of file keys
        """
        if not self.s3_client:
            logger.info(f"Simulating S3 list files (no AWS credentials): {prefix}")
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                files = [item['Key'] for item in response['Contents']]
            
            logger.info(f"Listed {len(files)} files from S3 with prefix: {prefix}")
            return files
        except Exception as e:
            logger.error(f"Error listing files from S3: {str(e)}")
            return []

# Create global storage service instance
storage_service = StorageService()
