set -e

echo "=== Environment Configuration for Railway Deployment ==="

if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "Running on Railway - Environment variables are automatically set by Railway."
    echo "Make sure to configure the following variables in your Railway project:"
    echo "- OPENAI_API_KEY: Your OpenAI API key"
    echo "- SECRET_KEY: A secure random string for session encryption"
    echo "- S3_ENDPOINT: Your S3-compatible storage endpoint"
    echo "- S3_ACCESS_KEY: Your S3 access key"
    echo "- S3_SECRET_KEY: Your S3 secret key"
    echo "- S3_BUCKET_NAME: Your S3 bucket name"
    echo "- S3_REGION: Your S3 region"
    exit 0
fi

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "Generated a random SECRET_KEY"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "Please enter your OpenAI API key:"
    read -p "> " OPENAI_API_KEY
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "Error: OpenAI API key is required."
        exit 1
    fi
fi

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup"
    echo "Backed up existing .env file to ${ENV_FILE}.backup"
fi

cat > "$ENV_FILE" << EOF
USE_POSTGRES=true
DATABASE_URL=\${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/short_form_video_accelerator}

OPENAI_API_KEY=$OPENAI_API_KEY

SECRET_KEY=$SECRET_KEY

S3_ENDPOINT=\${S3_ENDPOINT:-}
S3_ACCESS_KEY=\${S3_ACCESS_KEY:-}
S3_SECRET_KEY=\${S3_SECRET_KEY:-}
S3_BUCKET_NAME=\${S3_BUCKET_NAME:-}
S3_REGION=\${S3_REGION:-us-east-1}
EOF

echo "Environment configuration saved to $ENV_FILE"

echo "=== Railway Environment Configuration ==="
echo "To set these environment variables in Railway, use the Railway dashboard or CLI:"
echo "railway variables set OPENAI_API_KEY=$OPENAI_API_KEY"
echo "railway variables set SECRET_KEY=$SECRET_KEY"
echo "railway variables set USE_POSTGRES=true"
echo ""
echo "Note: DATABASE_URL will be automatically set by the PostgreSQL plugin."
echo "=== Configuration Complete ==="
