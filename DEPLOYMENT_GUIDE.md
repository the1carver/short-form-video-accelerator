# Short-Form Video Accelerator Deployment Guide

This comprehensive guide provides instructions for deploying the Short-Form Video Accelerator application to production environments. The application can be deployed to either Fly.io or DigitalOcean, depending on your preference.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
   - [Fly.io Deployment](#flyio-deployment)
   - [DigitalOcean Deployment](#digitalocean-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Environment Configuration](#environment-configuration)
5. [API Keys Setup](#api-keys-setup)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- Git repository access
- [Fly.io](https://fly.io) account (if deploying to Fly.io)
- [DigitalOcean](https://www.digitalocean.com/) account (if deploying to DigitalOcean)
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Google Cloud Platform](https://console.cloud.google.com/) account with Video Intelligence API enabled
- S3-compatible storage service (AWS S3, MinIO, or Fly.io Tigris)

## Backend Deployment

### Fly.io Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/the1carver/short-form-video-accelerator.git
   cd short-form-video-accelerator
   ```

2. **Install Fly.io CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

3. **Authenticate with Fly.io**
   ```bash
   fly auth login
   ```

4. **Run the deployment script**
   ```bash
   cd backend
   ./deploy.sh
   ```

   This script will:
   - Install dependencies
   - Set up Fly.io Tigris storage (if not already set up)
   - Deploy the application to Fly.io

5. **Configure environment variables**
   ```bash
   ./config_production_env.sh
   ```

### DigitalOcean Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/the1carver/short-form-video-accelerator.git
   cd short-form-video-accelerator
   ```

2. **Install DigitalOcean CLI**
   ```bash
   curl -sL https://github.com/digitalocean/doctl/releases/download/v1.92.1/doctl-1.92.1-linux-amd64.tar.gz | tar -xzv
   sudo mv doctl /usr/local/bin
   ```

3. **Authenticate with DigitalOcean**
   ```bash
   doctl auth init
   ```

4. **Run the deployment script**
   ```bash
   cd deployment/digitalocean
   ./deploy.sh
   ```

   This script will:
   - Build the frontend
   - Create or update the DigitalOcean App Platform application
   - Configure the deployment

5. **Configure environment variables**
   ```bash
   cd ../../backend
   ./config_production_env.sh
   ```

## Frontend Deployment

### Fly.io Frontend Deployment

1. **Build the frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Configure environment variables**
   ```bash
   ./config_production_env.sh
   ```

3. **Deploy to Fly.io**
   ```bash
   fly launch --name short-form-video-accelerator-frontend
   fly deploy
   ```

### DigitalOcean Frontend Deployment

The frontend is automatically deployed as part of the DigitalOcean App Platform configuration.

## Environment Configuration

### Configure Backend Environment

The backend environment configuration script (`backend/config_production_env.sh`) sets up the necessary environment variables for production deployment:

- `DATABASE_URL`: SQLite database URL
- `SECRET_KEY`: Secret key for session encryption
- `OPENAI_API_KEY`: OpenAI API key
- `S3_ENDPOINT`: S3-compatible storage endpoint
- `S3_ACCESS_KEY`: S3 access key
- `S3_SECRET_KEY`: S3 secret key
- `S3_BUCKET_NAME`: S3 bucket name
- `S3_REGION`: S3 region
- `GOOGLE_CREDENTIALS`: Google Cloud credentials

### Configure Frontend Environment

The frontend environment configuration script (`frontend/config_production_env.sh`) sets up the necessary environment variables for production deployment:

- `VITE_API_URL`: Backend API URL

## API Keys Setup

### Set Up OpenAI API Key

1. **Create an OpenAI account**
   Visit [OpenAI](https://platform.openai.com/) and create an account.

2. **Generate an API key**
   Go to the [API keys page](https://platform.openai.com/api-keys) and generate a new API key.

3. **Run the API key setup script**
   ```bash
   cd backend
   ./setup_api_keys.sh
   ```

### Set Up Google Video Intelligence API

1. **Create a Google Cloud project**
   Visit [Google Cloud Console](https://console.cloud.google.com/) and create a new project.

2. **Enable the Video Intelligence API**
   Go to the [API Library](https://console.cloud.google.com/apis/library) and enable the Video Intelligence API.

3. **Create a service account**
   Go to the [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts) and create a new service account.

4. **Generate a JSON key**
   Create a new key for the service account and download the JSON file.

5. **Run the API key setup script**
   ```bash
   cd backend
   GOOGLE_CREDENTIALS_FILE=/path/to/credentials.json ./setup_api_keys.sh
   ```

## Verification

After deployment, verify that the application is working correctly:

1. **Run the verification script**
   ```bash
   cd backend
   ./verify_deployment.sh
   ```

2. **Verify API keys**
   ```bash
   ./verify_api_keys.py
   ```

3. **Manual verification**
   - Visit the frontend URL in a browser
   - Test the login functionality
   - Upload a video and verify processing
   - Test the Visual Segment Editor
   - Test the Instant Clip feature
   - Test the Brand Settings

## Troubleshooting

### Fly.io Deployment Issues

- **Check logs**
  ```bash
  fly logs
  ```

- **SSH into the instance**
  ```bash
  fly ssh console
  ```

- **Verify environment variables**
  ```bash
  fly secrets list
  ```

### DigitalOcean Deployment Issues

- **Check logs**
  Go to the DigitalOcean App Platform dashboard and check the logs for your application.

- **Verify environment variables**
  Go to the DigitalOcean App Platform dashboard and check the environment variables for your application.

- **Component detection issues**
  If DigitalOcean App Platform fails to detect components:
  1. Verify Dockerfile location matches `source_dir` in app.spec.yaml
  2. Ensure changes are in the configured deployment branch
  3. Check environment variables are properly set in DigitalOcean
  4. Review App Platform deployment logs for specific failure reasons

### API Key Issues

- **OpenAI API key**
  Verify that the OpenAI API key is correctly set in the environment variables.

- **Google Video Intelligence API**
  Verify that the Google credentials file is correctly set in the environment variables.

- **S3 storage**
  Verify that the S3 storage configuration is correctly set in the environment variables.
