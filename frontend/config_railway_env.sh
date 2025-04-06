set -e

echo "=== Frontend Environment Configuration for Railway Deployment ==="

if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "Running on Railway - Environment variables are automatically set by Railway."
    echo "Make sure to configure the VITE_API_URL in your Railway project."
    exit 0
fi

if [ -z "$BACKEND_URL" ]; then
    echo "Please enter the URL of your deployed backend on Railway:"
    echo "(e.g., https://your-app-name.up.railway.app)"
    read -p "> " BACKEND_URL
    
    if [ -z "$BACKEND_URL" ]; then
        echo "Error: Backend URL is required."
        exit 1
    fi
fi

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup"
    echo "Backed up existing .env file to ${ENV_FILE}.backup"
fi

cat > "$ENV_FILE" << EOF
VITE_API_URL=$BACKEND_URL
EOF

echo "Frontend environment configuration saved to $ENV_FILE"

echo "=== Railway Environment Configuration ==="
echo "To set these environment variables in Railway, use the Railway dashboard or CLI:"
echo "railway variables set VITE_API_URL=$BACKEND_URL"
echo ""
echo "=== Configuration Complete ==="
