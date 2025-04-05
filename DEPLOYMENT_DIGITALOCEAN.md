# DigitalOcean Deployment Guide for Short-Form Video Accelerator

This guide provides instructions for deploying the Short-Form Video Accelerator application to DigitalOcean App Platform.

## Prerequisites

- [DigitalOcean](https://www.digitalocean.com/) account
- [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) CLI tool installed
- GitHub repository connected to DigitalOcean App Platform

## Deployment Steps

### 1. Prepare the Application Specification

The application specification is defined in `deployment/digitalocean/app.spec.yaml`. This file contains the configuration for both the frontend and backend services.

### 2. Configure Environment Variables

Before deploying, you need to set up the following environment variables as secrets in DigitalOcean App Platform:

- `SECRET_KEY`: A secure random string for session encryption
- `OPENAI_API_KEY`: Your OpenAI API key
- `S3_ENDPOINT`: S3-compatible storage endpoint
- `S3_ACCESS_KEY`: S3 access key
- `S3_SECRET_KEY`: S3 secret key
- `S3_BUCKET_NAME`: S3 bucket name
- `S3_REGION`: S3 region
- `GOOGLE_CREDENTIALS`: JSON string containing Google Cloud credentials

### 3. Deploy Using App Platform

#### Option 1: Using the DigitalOcean Dashboard

1. Log in to your DigitalOcean account
2. Navigate to App Platform
3. Click "Create App"
4. Select your GitHub repository
5. Choose the branch to deploy from (default: main)
6. DigitalOcean will automatically detect the components based on the repository structure
7. Configure the environment variables as secrets
8. Review and create the app

#### Option 2: Using the Command Line

1. Install and authenticate the DigitalOcean CLI:
   ```bash
   doctl auth init
   ```

2. Create the app from the specification file:
   ```bash
   doctl apps create --spec deployment/digitalocean/app.spec.yaml
   ```

3. Check the deployment status:
   ```bash
   doctl apps list
   ```

### 4. Troubleshooting Component Detection

If DigitalOcean App Platform fails to detect components:

1. Verify Dockerfile location matches `source_dir` in app.spec.yaml
2. Ensure changes are in the configured deployment branch
3. Check environment variables are properly set in DigitalOcean
4. Review App Platform deployment logs for specific failure reasons

## Monitoring and Maintenance

### View Logs

1. In the DigitalOcean dashboard, navigate to your app
2. Select the component (frontend or backend)
3. Click on "Logs" to view the application logs

### Update the Application

To update the application:

1. Push changes to the configured branch in your GitHub repository
2. DigitalOcean will automatically deploy the changes if `deploy_on_push` is set to `true`
3. Monitor the deployment in the DigitalOcean dashboard

### Scale the Application

1. In the DigitalOcean dashboard, navigate to your app
2. Select the component to scale
3. Click on "Settings" and adjust the instance count or size

## Additional Resources

- [DigitalOcean App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [App Specification Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)
