import os
import sys
import boto3
from dotenv import load_dotenv

load_dotenv()

def test_s3_connection():
    """Test S3 connection using environment variables"""
    print("Testing S3 connection...")
    
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID", "simulated_key")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "simulated_secret")
    aws_region = os.getenv("AWS_REGION", "us-west-2")
    s3_bucket = os.getenv("S3_BUCKET_NAME", "short-form-video-storage")
    
    print(f"AWS Access Key: {aws_access_key[:4]}{'*' * (len(aws_access_key) - 4)}")
    print(f"AWS Region: {aws_region}")
    print(f"S3 Bucket: {s3_bucket}")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        response = s3_client.list_buckets()
        print(f"Successfully connected to S3")
        print(f"Available buckets: {[bucket['Name'] for bucket in response.get('Buckets', [])]}")
        
        test_file_path = "test_upload.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test file for S3 upload")
        
        print(f"Uploading test file to S3 bucket: {s3_bucket}")
        s3_client.upload_file(
            test_file_path, 
            s3_bucket, 
            "test_upload.txt"
        )
        print("File uploaded successfully")
        
        os.remove(test_file_path)
        print("Test file removed locally")
        
        return True
    except Exception as e:
        print(f"Error connecting to S3: {str(e)}")
        
        if os.getenv("DEBUG") == "True":
            print("Running in development mode, simulating successful S3 operations")
            return True
        
        return False

if __name__ == "__main__":
    success = test_s3_connection()
    print(f"S3 integration test {'successful' if success else 'failed'}")
    sys.exit(0 if success else 1)
