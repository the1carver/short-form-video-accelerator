set -e

echo "=== PostgreSQL Setup for Short-Form Video Accelerator ==="

if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "Running on Railway - PostgreSQL is automatically configured."
    echo "Database URL: ${DATABASE_URL:-Not set}"
    
    echo "Creating database tables..."
    python migrations/create_tables.py
    
    echo "PostgreSQL setup complete."
    exit 0
fi

echo "Setting up PostgreSQL for local development..."

if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
fi

if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
fi

DB_NAME="short_form_video_accelerator"
DB_USER="postgres"
DB_PASSWORD="postgres"

if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database: $DB_NAME"
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
    echo "Database created successfully."
else
    echo "Database $DB_NAME already exists."
fi

export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
export USE_POSTGRES=true

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$DATABASE_URL|g" "$ENV_FILE"
    else
        echo "DATABASE_URL=$DATABASE_URL" >> "$ENV_FILE"
    fi
    
    if grep -q "^USE_POSTGRES=" "$ENV_FILE"; then
        sed -i "s|^USE_POSTGRES=.*|USE_POSTGRES=true|g" "$ENV_FILE"
    else
        echo "USE_POSTGRES=true" >> "$ENV_FILE"
    fi
else
    cat > "$ENV_FILE" << EOF
DATABASE_URL=$DATABASE_URL
USE_POSTGRES=true
EOF
fi

echo "Environment variables set:"
echo "DATABASE_URL=$DATABASE_URL"
echo "USE_POSTGRES=true"

echo "Creating database tables..."
python migrations/create_tables.py

echo "=== PostgreSQL Setup Complete ==="
echo "You can now run the application with PostgreSQL database."
