# Railway Deployment Guide for Short-Form Video Accelerator

This guide provides instructions for deploying the Short-Form Video Accelerator application to Railway.

## Prerequisites

- [Railway](https://railway.app/) account
- GitHub repository connected to Railway
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Google Cloud Platform](https://console.cloud.google.com/) account with Video Intelligence API enabled

## Automated Deployment

We've created deployment scripts to simplify the process of deploying to Railway.

### 1. Backend Deployment

```bash
cd short-form-video-accelerator/backend
chmod +x deploy_railway.sh
./deploy_railway.sh
```

This script will:
- Install Railway CLI if needed
- Set up environment variables
- Configure the OpenAI API key
- Deploy the backend to Railway
- Update the frontend environment with the backend URL

### 2. Frontend Deployment

```bash
cd short-form-video-accelerator/frontend
chmod +x deploy_railway.sh
./deploy_railway.sh
```

This script will:
- Install Railway CLI if needed
- Build the frontend
- Set up environment variables
- Deploy the frontend to Railway

## Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### 1. Backend Deployment

1. **Create a new Railway project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure the service**
   - Railway will automatically detect the configuration from `railway.json` and `backend/railway.toml`
   - Set the root directory to `/backend`

3. **Add PostgreSQL database**
   - Click "New" and select "Database"
   - Choose "PostgreSQL"
   - Railway will automatically create a PostgreSQL instance and add the connection variables to your project

4. **Configure environment variables**
   - Go to the "Variables" tab of your service
   - Add the following variables:
     - `SECRET_KEY`: A secure random string for session encryption
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `GOOGLE_CREDENTIALS`: JSON string containing Google Cloud credentials
     - `USE_POSTGRES`: Set to `true`
     - `DATABASE_URL`: This should be automatically set by Railway when you add the PostgreSQL plugin

### 2. Frontend Deployment

1. **Create a new service in your Railway project**
   - Click "New" and select "Service"
   - Choose "GitHub Repo" and select the same repository
   - Set the root directory to `/frontend`

2. **Configure the service**
   - Set the build command: `npm install && npm run build`
   - Set the start command: `npx serve -s dist`

3. **Configure environment variables**
   - Go to the "Variables" tab of your frontend service
   - Add the following variable:
     - `VITE_API_URL`: The URL of your backend service (e.g., `https://your-backend-service.railway.app`)

### 3. Set Up Storage

Railway doesn't provide built-in object storage like S3, so you have two options:

#### Option 1: Use AWS S3

1. **Create an AWS S3 bucket**
   - Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
   - Create a new bucket
   - Configure CORS settings to allow requests from your Railway app

2. **Add S3 environment variables to your backend service**
   - `S3_ENDPOINT`: `https://s3.amazonaws.com`
   - `S3_ACCESS_KEY`: Your AWS access key
   - `S3_SECRET_KEY`: Your AWS secret key
   - `S3_BUCKET_NAME`: Your S3 bucket name
   - `S3_REGION`: Your S3 bucket region

#### Option 2: Use MinIO on Railway

1. **Create a new service in your Railway project**
   - Click "New" and select "Service"
   - Choose "Template" and select "MinIO"

2. **Add MinIO environment variables to your backend service**
   - `S3_ENDPOINT`: The URL of your MinIO service
   - `S3_ACCESS_KEY`: The access key from your MinIO service variables
   - `S3_SECRET_KEY`: The secret key from your MinIO service variables
   - `S3_BUCKET_NAME`: A bucket name of your choice
   - `S3_REGION`: `us-east-1` (default for MinIO)

## Verify Deployment

After deployment, verify that the application is working correctly:

1. **Run the verification script**
   ```bash
   cd backend
   python verify_railway_env.py
   ```

2. **Check service status**
   - Go to the "Deployments" tab of each service
   - Verify that the deployment was successful

3. **Test the application**
   - Click on the URL of your frontend service
   - Test the login functionality
   - Upload a video and verify processing
   - Test the Visual Segment Editor
   - Test the Instant Clip feature
   - Test the Brand Settings

## Troubleshooting

### Deployment Issues

- **Check logs**
  - Go to the "Deployments" tab of the service
  - Click on the deployment to view logs

- **Environment variables**
  - Verify that all required environment variables are set correctly
  - Check for typos in variable names

### Database Issues

- **Connection errors**
  - Verify that the `DATABASE_URL` is correctly set
  - Check if the PostgreSQL service is running

### Storage Issues

- **S3 connection errors**
  - Verify that all S3 environment variables are set correctly
  - Check CORS settings on your S3 bucket

## Maintenance

### Updating the Application

1. **Push changes to your GitHub repository**
   - Railway will automatically deploy the changes

2. **Monitor deployments**
   - Go to the "Deployments" tab to monitor the deployment status

### Scaling

Railway automatically scales your application based on usage. You can upgrade your plan for more resources if needed.

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Railway GitHub Integration](https://docs.railway.app/deploy/github)
