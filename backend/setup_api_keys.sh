set -e


echo "=== API Key Setup for Short-Form Video Accelerator ==="
echo "This script will help you set up the required API keys for OpenAI and Google Video Intelligence."

if [ -n "$FLY_APP_NAME" ]; then
  PLATFORM="fly.io"
  echo "Detected Fly.io deployment platform."
else
  echo "No specific platform detected. Will create local .env file."
  PLATFORM="local"
fi

echo ""
echo "=== OpenAI API Key Setup ==="
echo "The OpenAI API key is required for AI-powered content analysis and generation."
echo "You can get an API key from https://platform.openai.com/api-keys"

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Please enter your OpenAI API key:"
  read -p "> " OPENAI_API_KEY
  
  if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OpenAI API key is required."
    exit 1
  fi
else
  echo "Using OpenAI API key from environment variable."
fi

echo ""
echo "=== Google Video Intelligence API Setup ==="
echo "The Google Video Intelligence API is used for advanced video analysis."
echo "You need a Google Cloud service account with Video Intelligence API access."
echo "Learn more: https://cloud.google.com/video-intelligence/docs/setup"

if [ -z "$GOOGLE_CREDENTIALS_FILE" ]; then
  echo "Please enter the path to your Google credentials JSON file:"
  read -p "> " GOOGLE_CREDENTIALS_FILE
  
  if [ -z "$GOOGLE_CREDENTIALS_FILE" ] || [ ! -f "$GOOGLE_CREDENTIALS_FILE" ]; then
    echo "Warning: Google credentials file not provided or not found."
    echo "You can set it up later by updating the environment variables."
  fi
else
  echo "Using Google credentials file from environment variable."
fi

if [ "$PLATFORM" = "fly.io" ]; then
  echo ""
  echo "=== Setting up API keys on Fly.io ==="
  
  echo "Setting OpenAI API key..."
  fly secrets set OPENAI_API_KEY="$OPENAI_API_KEY"
  
  if [ -n "$GOOGLE_CREDENTIALS_FILE" ] && [ -f "$GOOGLE_CREDENTIALS_FILE" ]; then
    echo "Setting Google credentials..."
    fly secrets set GOOGLE_CREDENTIALS="$(cat "$GOOGLE_CREDENTIALS_FILE")"
  fi
  
  echo "API keys have been set up on Fly.io."
  echo "You can verify them with: fly secrets list"
  
else
  echo ""
  echo "=== Setting up API keys locally ==="
  
  ENV_FILE=".env"
  
  if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup"
    echo "Backed up existing .env file to ${ENV_FILE}.backup"
  fi
  
  if grep -q "OPENAI_API_KEY" "$ENV_FILE" 2>/dev/null; then
    sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|g" "$ENV_FILE"
  else
    echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> "$ENV_FILE"
  fi
  
  if [ -n "$GOOGLE_CREDENTIALS_FILE" ] && [ -f "$GOOGLE_CREDENTIALS_FILE" ]; then
    echo "GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_CREDENTIALS_FILE" >> "$ENV_FILE"
  fi
  
  echo "API keys have been set up in $ENV_FILE"
fi

echo ""
echo "=== API Key Setup Complete ==="
echo "The application is now configured with the necessary API keys."
