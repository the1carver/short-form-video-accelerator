set -e


if [ -n "$FLY_APP_NAME" ]; then
  PLATFORM="fly.io"
  BACKEND_URL="https://$FLY_APP_NAME.fly.dev"
elif [ -n "$DIGITALOCEAN_APP_NAME" ]; then
  PLATFORM="digitalocean"
  BACKEND_URL="\${APP_URL}/api"
else
  echo "No platform detected. Please provide the backend URL:"
  read -p "Backend URL (e.g., https://your-app.fly.dev): " BACKEND_URL
fi

echo "Configuring frontend environment for $PLATFORM..."

cat > .env << EOF
VITE_API_URL=$BACKEND_URL
EOF

echo "Frontend environment configuration completed."
echo "Created .env file with the following content:"
cat .env

if [ "$PLATFORM" = "digitalocean" ] && [ -f "../deployment/digitalocean/app.spec.yaml" ]; then
  echo "Updating DigitalOcean App Platform configuration..."
  sed -i "s|VITE_API_URL=.*|VITE_API_URL=$BACKEND_URL|g" "../deployment/digitalocean/app.spec.yaml"
  echo "Updated DigitalOcean App Platform configuration."
fi

echo "To build the frontend for production, run:"
echo "  npm run build"
echo "This will create a 'dist' directory with the production build."
