"""
Verify API Keys Script for Short-Form Video Accelerator

This script verifies that the OpenAI and Google Video Intelligence API keys
are correctly configured and working.
"""

import os
import sys
import json
from dotenv import load_dotenv
import requests

load_dotenv()

def check_openai_api_key():
    """Check if the OpenAI API key is configured and working."""
    print("Checking OpenAI API key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found in environment variables.")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello, this is a test message."}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("✅ OpenAI API key is valid and working.")
            return True
        else:
            print(f"❌ OpenAI API key test failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing OpenAI API key: {str(e)}")
        return False

def check_google_credentials():
    """Check if Google credentials are configured."""
    print("Checking Google Video Intelligence API credentials...")
    
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not found in environment variables.")
        return False
    
    if not os.path.exists(credentials_path):
        print(f"❌ Google credentials file not found at: {credentials_path}")
        return False
    
    try:
        with open(credentials_path, 'r') as f:
            credentials = json.load(f)
        
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if field not in credentials]
        
        if missing_fields:
            print(f"❌ Google credentials file is missing required fields: {', '.join(missing_fields)}")
            return False
        
        print("✅ Google credentials file is valid.")
        
        print("ℹ️ To fully verify Google Video Intelligence API, you should run a test with an actual video file.")
        return True
    
    except json.JSONDecodeError:
        print(f"❌ Google credentials file is not valid JSON: {credentials_path}")
        return False
    except Exception as e:
        print(f"❌ Error checking Google credentials: {str(e)}")
        return False

def check_fly_io_secrets():
    """Check if API keys are set as secrets on Fly.io."""
    print("Checking Fly.io secrets...")
    
    if not os.getenv("FLY_APP_NAME"):
        print("ℹ️ Not running on Fly.io, skipping Fly.io secrets check.")
        return True
    
    try:
        import subprocess
        result = subprocess.run(["fly", "secrets", "list"], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error listing Fly.io secrets: {result.stderr}")
            return False
        
        secrets_output = result.stdout
        if "OPENAI_API_KEY" not in secrets_output:
            print("❌ OPENAI_API_KEY not found in Fly.io secrets.")
            return False
        
        if "GOOGLE_CREDENTIALS" not in secrets_output:
            print("❌ GOOGLE_CREDENTIALS not found in Fly.io secrets.")
            return False
        
        print("✅ API keys are correctly set as secrets on Fly.io.")
        return True
    
    except Exception as e:
        print(f"❌ Error checking Fly.io secrets: {str(e)}")
        return False

def main():
    """Main function to verify API keys."""
    print("=== API Key Verification for Short-Form Video Accelerator ===")
    
    openai_success = check_openai_api_key()
    google_success = check_google_credentials()
    flyio_success = check_fly_io_secrets()
    
    print("\n=== Verification Summary ===")
    print(f"OpenAI API Key: {'✅ Valid' if openai_success else '❌ Invalid'}")
    print(f"Google Credentials: {'✅ Valid' if google_success else '❌ Invalid'}")
    print(f"Fly.io Secrets: {'✅ Valid' if flyio_success else '❌ Invalid'}")
    
    if openai_success and google_success and flyio_success:
        print("\n✅ All API keys are correctly configured.")
        return 0
    else:
        print("\n❌ Some API keys are not correctly configured. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
