

echo "Setting up Fly.io Tigris storage..."

echo "Creating public storage bucket..."
fly storage create --public

echo "Verifying secrets..."
fly secrets list

echo "Storage setup complete!"
echo "To deploy the application, run: fly deploy"
echo ""
echo "Make sure to set the following environment variables in your frontend:"
echo "VITE_API_URL=https://short-form-video-accelerator.fly.dev"
