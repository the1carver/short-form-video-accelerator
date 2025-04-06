"""
Verify Railway environment variables for Short-Form Video Accelerator
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_environment_variables():
    """Check if all required environment variables are set"""
    required_vars = {
        "DATABASE_URL": "PostgreSQL connection string",
        "OPENAI_API_KEY": "OpenAI API key",
        "SECRET_KEY": "Secret key for session encryption",
        "USE_POSTGRES": "Flag to use PostgreSQL (should be 'true')"
    }
    
    optional_vars = {
        "S3_ENDPOINT": "S3-compatible storage endpoint",
        "S3_ACCESS_KEY": "S3 access key",
        "S3_SECRET_KEY": "S3 secret key",
        "S3_BUCKET_NAME": "S3 bucket name",
        "S3_REGION": "S3 region"
    }
    
    missing_required = []
    missing_optional = []
    
    print("=== Railway Environment Variables Check ===")
    
    print("\nRequired Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var in ["OPENAI_API_KEY", "SECRET_KEY", "S3_ACCESS_KEY", "S3_SECRET_KEY"]:
                masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set - {description}")
            missing_required.append(var)
    
    print("\nOptional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if var in ["S3_ACCESS_KEY", "S3_SECRET_KEY"]:
                masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: Not set - {description}")
            missing_optional.append(var)
    
    print("\nRailway-Specific Variables:")
    if os.getenv("RAILWAY_ENVIRONMENT"):
        print(f"✅ RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
    else:
        print("⚠️ RAILWAY_ENVIRONMENT: Not set - Not running on Railway")
    
    if os.getenv("PORT"):
        print(f"✅ PORT: {os.getenv('PORT')}")
    else:
        print("⚠️ PORT: Not set - Will use default port")
    
    print("\n=== Environment Check Summary ===")
    if missing_required:
        print(f"❌ Missing required variables: {', '.join(missing_required)}")
        print("These variables must be set for the application to function properly.")
        return False
    else:
        print("✅ All required variables are set.")
    
    if missing_optional:
        print(f"⚠️ Missing optional variables: {', '.join(missing_optional)}")
        if "S3_ENDPOINT" in missing_optional:
            print("Note: S3 storage functionality will not be available without S3 configuration.")
    else:
        print("✅ All optional variables are set.")
    
    return len(missing_required) == 0

def main():
    """Main function"""
    print("Verifying Railway environment variables...")
    
    if check_environment_variables():
        print("\n✅ Environment is properly configured for Railway deployment.")
        return 0
    else:
        print("\n❌ Environment is not properly configured for Railway deployment.")
        print("Please set the missing required variables before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
