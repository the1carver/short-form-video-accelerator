set -e

echo "=== Railway Deployment for Short-Form Video Accelerator Frontend ==="

if ! command -v railway &> /dev/null; then
    echo "Railway CLI is not installed. Installing..."
    npm i -g @railway/cli
fi

if ! railway whoami &> /dev/null; then
    echo "Please log in to Railway:"
    railway login
fi

echo "Installing dependencies..."
npm install

echo "Building frontend..."
npm run build

echo "Setting up environment variables..."
./config_railway_env.sh

if [ ! -f ".railway" ]; then
    echo "Linking to Railway project..."
    railway link
fi

echo "Deploying to Railway..."
railway up

echo "Getting deployment URL..."
RAILWAY_URL=$(railway status --json | jq -r '.url')

if [ -n "$RAILWAY_URL" ]; then
    echo "Frontend deployed successfully to: $RAILWAY_URL"
else
    echo "Failed to get deployment URL. Please check the Railway dashboard."
fi

echo "=== Railway Deployment Complete ==="
