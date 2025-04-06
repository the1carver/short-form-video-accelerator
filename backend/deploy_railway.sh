set -e

echo "=== Railway Deployment for Short-Form Video Accelerator Backend ==="

if ! command -v railway &> /dev/null; then
    echo "Railway CLI is not installed. Installing..."
    npm i -g @railway/cli
fi

if ! railway whoami &> /dev/null; then
    echo "Please log in to Railway:"
    railway login
fi

echo "Setting up environment variables..."
./config_railway_env.sh

if [ -n "$OPENAI_API_KEY" ]; then
    echo "Setting up OpenAI API key..."
    ./setup_openai_key.sh "$OPENAI_API_KEY"
fi

echo "Verifying environment variables..."
python verify_railway_env.py

if [ ! -f ".railway" ]; then
    echo "Linking to Railway project..."
    railway link
fi

echo "Deploying to Railway..."
railway up

echo "Getting deployment URL..."
RAILWAY_URL=$(railway status --json | jq -r '.url')

if [ -n "$RAILWAY_URL" ]; then
    echo "Backend deployed successfully to: $RAILWAY_URL"
    
    echo "Updating frontend environment..."
    cd ../frontend
    BACKEND_URL="$RAILWAY_URL" ./config_railway_env.sh
else
    echo "Failed to get deployment URL. Please check the Railway dashboard."
fi

echo "=== Railway Deployment Complete ==="
echo "You can now deploy the frontend to Railway or another platform."
