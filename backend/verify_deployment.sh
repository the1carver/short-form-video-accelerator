set -e


echo "=== Deployment Verification for Short-Form Video Accelerator ==="

if [ -n "$FLY_APP_NAME" ]; then
  PLATFORM="fly.io"
  BACKEND_URL="https://$FLY_APP_NAME.fly.dev"
  echo "Detected Fly.io deployment platform."
elif [ -n "$DIGITALOCEAN_APP_NAME" ]; then
  PLATFORM="digitalocean"
  BACKEND_URL="https://$DIGITALOCEAN_APP_NAME.ondigitalocean.app/api"
  echo "Detected DigitalOcean deployment platform."
else
  echo "No specific platform detected. Please enter the backend URL:"
  read -p "> " BACKEND_URL
fi

echo "Backend URL: $BACKEND_URL"

echo ""
echo "=== Verifying Backend Deployment ==="
echo "Checking if backend is accessible..."

if command -v curl &> /dev/null; then
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
  
  if [ "$RESPONSE" = "200" ]; then
    echo "✅ Backend is accessible and healthy."
  else
    echo "❌ Backend health check failed with status code: $RESPONSE"
    echo "Please check the backend deployment and logs."
  fi
else
  echo "❌ curl command not found. Please install curl to verify the backend."
fi

echo ""
echo "=== Verifying Frontend Deployment ==="

if [ "$PLATFORM" = "fly.io" ]; then
  FRONTEND_URL="https://short-form-video-accelerator-frontend.fly.dev"
elif [ "$PLATFORM" = "digitalocean" ]; then
  FRONTEND_URL="https://$DIGITALOCEAN_APP_NAME.ondigitalocean.app"
else
  echo "Please enter the frontend URL:"
  read -p "> " FRONTEND_URL
fi

echo "Frontend URL: $FRONTEND_URL"
echo "Checking if frontend is accessible..."

if command -v curl &> /dev/null; then
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
  
  if [ "$RESPONSE" = "200" ]; then
    echo "✅ Frontend is accessible."
  else
    echo "❌ Frontend check failed with status code: $RESPONSE"
    echo "Please check the frontend deployment and logs."
  fi
else
  echo "❌ curl command not found. Please install curl to verify the frontend."
fi

echo ""
echo "=== Verifying API Connectivity ==="
echo "Checking if frontend can connect to backend API..."

if command -v curl &> /dev/null; then
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/content")
  
  if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "401" ]; then
    echo "✅ Backend API is responding (status code: $RESPONSE)."
  else
    echo "❌ Backend API check failed with status code: $RESPONSE"
    echo "Please check the API configuration and logs."
  fi
else
  echo "❌ curl command not found. Please install curl to verify the API connectivity."
fi

echo ""
echo "=== Verifying Environment Variables ==="

if [ "$PLATFORM" = "fly.io" ]; then
  echo "Checking Fly.io environment variables..."
  
  if command -v fly &> /dev/null; then
    SECRETS=$(fly secrets list)
    
    if echo "$SECRETS" | grep -q "OPENAI_API_KEY"; then
      echo "✅ OPENAI_API_KEY is set."
    else
      echo "❌ OPENAI_API_KEY is not set."
    fi
    
    if echo "$SECRETS" | grep -q "S3_BUCKET_NAME"; then
      echo "✅ S3 storage configuration is set."
    else
      echo "❌ S3 storage configuration is not set."
    fi
    
    if echo "$SECRETS" | grep -q "GOOGLE_CREDENTIALS"; then
      echo "✅ GOOGLE_CREDENTIALS is set."
    else
      echo "❌ GOOGLE_CREDENTIALS is not set."
    fi
  else
    echo "❌ fly command not found. Please install the Fly.io CLI to verify environment variables."
  fi
elif [ "$PLATFORM" = "digitalocean" ]; then
  echo "To verify DigitalOcean environment variables, please check the App Platform dashboard."
  echo "Visit: https://cloud.digitalocean.com/apps"
else
  echo "Please verify environment variables manually for your deployment platform."
fi

echo ""
echo "=== Deployment Verification Summary ==="
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "To complete verification:"
echo "1. Visit the frontend URL in a browser"
echo "2. Test the login functionality"
echo "3. Upload a video and verify processing"
echo "4. Test the Visual Segment Editor"
echo "5. Test the Instant Clip feature"
echo "6. Test the Brand Settings"
echo ""
echo "For detailed logs:"
if [ "$PLATFORM" = "fly.io" ]; then
  echo "- Backend logs: fly logs -a $FLY_APP_NAME"
  echo "- Frontend logs: fly logs -a short-form-video-accelerator-frontend"
elif [ "$PLATFORM" = "digitalocean" ]; then
  echo "- Check logs in the DigitalOcean App Platform dashboard"
fi
