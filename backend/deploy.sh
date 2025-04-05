

echo "Deploying Short-Form Video Accelerator backend to Fly.io..."

echo "Installing dependencies..."
poetry install

if [ ! -f ".storage_setup_complete" ]; then
  echo "Setting up storage..."
  ./setup_storage.sh
  touch .storage_setup_complete
fi

echo "Deploying application..."
fly deploy

echo "Deployment complete!"
echo "Your application is now available at: https://short-form-video-accelerator.fly.dev"
