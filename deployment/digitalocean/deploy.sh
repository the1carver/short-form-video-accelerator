set -e


if ! command -v doctl &> /dev/null; then
    echo "Error: doctl is not installed. Please install it first."
    echo "Visit: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

if ! doctl account get &> /dev/null; then
    echo "Error: You are not authenticated with DigitalOcean."
    echo "Please run 'doctl auth init' and try again."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Short-Form Video Accelerator Deployment ==="
echo "Project root: $PROJECT_ROOT"

echo "Building frontend..."
cd "$PROJECT_ROOT/frontend"
npm install
npm run build

APP_NAME="short-form-video-accelerator"
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -n "$APP_ID" ]; then
    echo "App '$APP_NAME' already exists with ID: $APP_ID"
    echo "Updating existing app..."
    doctl apps update "$APP_ID" --spec "$SCRIPT_DIR/app.spec.yaml"
else
    echo "Creating new app '$APP_NAME'..."
    doctl apps create --spec "$SCRIPT_DIR/app.spec.yaml"
fi

echo "Deployment initiated. Check status with: doctl apps list"
echo "Once deployed, view your app at: https://short-form-video-accelerator.ondigitalocean.app"
