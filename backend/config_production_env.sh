set -e


if [ -n "$FLY_APP_NAME" ]; then
  PLATFORM="fly.io"
elif [ -n "$DIGITALOCEAN_APP_NAME" ]; then
  PLATFORM="digitalocean"
else
  echo "Error: Unknown deployment platform. This script is intended for Fly.io or DigitalOcean."
  exit 1
fi

echo "Configuring production environment for $PLATFORM..."

SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL="sqlite:///./app.db"

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Error: OPENAI_API_KEY environment variable is required."
  echo "Please set it before running this script:"
  echo "  export OPENAI_API_KEY=your-openai-api-key"
  exit 1
fi

if [ "$PLATFORM" = "fly.io" ]; then
  echo "Setting up Fly.io environment variables..."
  
  fly secrets set DATABASE_URL="$DATABASE_URL"
  fly secrets set SECRET_KEY="$SECRET_KEY"
  fly secrets set OPENAI_API_KEY="$OPENAI_API_KEY"
  
  if [ -n "$S3_ENDPOINT" ] && [ -n "$S3_ACCESS_KEY" ] && [ -n "$S3_SECRET_KEY" ] && [ -n "$S3_BUCKET_NAME" ] && [ -n "$S3_REGION" ]; then
    fly secrets set S3_ENDPOINT="$S3_ENDPOINT"
    fly secrets set S3_ACCESS_KEY="$S3_ACCESS_KEY"
    fly secrets set S3_SECRET_KEY="$S3_SECRET_KEY"
    fly secrets set S3_BUCKET_NAME="$S3_BUCKET_NAME"
    fly secrets set S3_REGION="$S3_REGION"
  else
    echo "Warning: S3 storage environment variables not fully provided."
    echo "You will need to set them manually using 'fly secrets set'."
  fi
  
  if [ -n "$GOOGLE_CREDENTIALS_FILE" ]; then
    if [ -f "$GOOGLE_CREDENTIALS_FILE" ]; then
      fly secrets set GOOGLE_CREDENTIALS="$(cat "$GOOGLE_CREDENTIALS_FILE")"
    else
      echo "Error: Google credentials file not found at $GOOGLE_CREDENTIALS_FILE"
      exit 1
    fi
  else
    echo "Warning: GOOGLE_CREDENTIALS_FILE not provided."
    echo "You will need to set GOOGLE_CREDENTIALS manually using 'fly secrets set'."
  fi
  
  echo "Verifying Fly.io secrets..."
  fly secrets list
  
elif [ "$PLATFORM" = "digitalocean" ]; then
  echo "Setting up DigitalOcean environment variables..."
  
  TMP_APP_YAML=$(mktemp)
  cat > "$TMP_APP_YAML" << EOF
name: short-form-video-accelerator
region: nyc
services:
  - name: short-form-video-accelerator-backend
    github:
      repo: the1carver/short-form-video-accelerator
      branch: main
      deploy_on_push: true
    source_dir: backend
    dockerfile_path: Dockerfile
    http_port: 8000
    instance_count: 2
    instance_size_slug: basic-xs
    routes:
      - path: /api
    envs:
      - key: DATABASE_URL
        value: $DATABASE_URL
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
        value: $SECRET_KEY
      - key: OPENAI_API_KEY
        scope: RUN_TIME
        type: SECRET
        value: $OPENAI_API_KEY
EOF
  
  if [ -n "$S3_ENDPOINT" ] && [ -n "$S3_ACCESS_KEY" ] && [ -n "$S3_SECRET_KEY" ] && [ -n "$S3_BUCKET_NAME" ] && [ -n "$S3_REGION" ]; then
    cat >> "$TMP_APP_YAML" << EOF
      - key: S3_ENDPOINT
        scope: RUN_TIME
        type: SECRET
        value: $S3_ENDPOINT
      - key: S3_ACCESS_KEY
        scope: RUN_TIME
        type: SECRET
        value: $S3_ACCESS_KEY
      - key: S3_SECRET_KEY
        scope: RUN_TIME
        type: SECRET
        value: $S3_SECRET_KEY
      - key: S3_BUCKET_NAME
        scope: RUN_TIME
        type: SECRET
        value: $S3_BUCKET_NAME
      - key: S3_REGION
        scope: RUN_TIME
        type: SECRET
        value: $S3_REGION
EOF
  else
    echo "Warning: S3 storage environment variables not fully provided."
    echo "You will need to set them manually in the DigitalOcean dashboard."
  fi
  
  if [ -n "$GOOGLE_CREDENTIALS_FILE" ] && [ -f "$GOOGLE_CREDENTIALS_FILE" ]; then
    GOOGLE_CREDS=$(cat "$GOOGLE_CREDENTIALS_FILE" | base64)
    cat >> "$TMP_APP_YAML" << EOF
      - key: GOOGLE_CREDENTIALS
        scope: RUN_TIME
        type: SECRET
        value: $GOOGLE_CREDS
EOF
  else
    echo "Warning: GOOGLE_CREDENTIALS_FILE not provided or file not found."
    echo "You will need to set GOOGLE_CREDENTIALS manually in the DigitalOcean dashboard."
  fi
  
  cat >> "$TMP_APP_YAML" << EOF

  - name: short-form-video-accelerator-frontend
    github:
      repo: the1carver/short-form-video-accelerator
      branch: main
      deploy_on_push: true
    source_dir: frontend
    build_command: npm install && npm run build
    output_dir: dist
    envs:
      - key: VITE_API_URL
        value: \${APP_URL}/api
    routes:
      - path: /
EOF
  
  echo "Applying DigitalOcean App Platform configuration..."
  doctl apps create --spec "$TMP_APP_YAML"
  
  rm "$TMP_APP_YAML"
fi

echo "Production environment configuration completed for $PLATFORM."
