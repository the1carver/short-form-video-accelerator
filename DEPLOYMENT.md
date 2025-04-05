# Short-Form Video Accelerator Deployment Guide

This document provides instructions for deploying the Short-Form Video Accelerator application to production environments.

## Prerequisites

- [Fly.io](https://fly.io) account for backend deployment
- Static hosting service (Vercel, Netlify, or AWS S3) for frontend deployment
- S3-compatible storage service (AWS S3, MinIO, or Fly.io Tigris)
- OpenAI API key
- Google Cloud Platform account with Video Intelligence API enabled

## Backend Deployment (Fly.io)

1. **Install Fly.io CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Authenticate with Fly.io**
   ```bash
   fly auth login
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the backend directory with the following variables:
   ```
   DATABASE_URL=sqlite:///./app.db
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-api-key
   GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json
   S3_ENDPOINT=your-s3-endpoint
   S3_ACCESS_KEY=your-s3-access-key
   S3_SECRET_KEY=your-s3-secret-key
   S3_BUCKET_NAME=your-s3-bucket-name
   S3_REGION=your-s3-region
   ```

4. **Deploy to Fly.io**
   ```bash
   cd backend
   fly deploy
   ```

5. **Set Environment Variables on Fly.io**
   ```bash
   fly secrets set DATABASE_URL=sqlite:///./app.db
   fly secrets set SECRET_KEY=your-secret-key
   fly secrets set OPENAI_API_KEY=your-openai-api-key
   fly secrets set S3_ENDPOINT=your-s3-endpoint
   fly secrets set S3_ACCESS_KEY=your-s3-access-key
   fly secrets set S3_SECRET_KEY=your-s3-secret-key
   fly secrets set S3_BUCKET_NAME=your-s3-bucket-name
   fly secrets set S3_REGION=your-s3-region
   ```

6. **Upload Google Credentials**
   ```bash
   fly secrets set GOOGLE_CREDENTIALS="$(cat path/to/google-credentials.json)"
   ```

## Frontend Deployment

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Authenticate with Vercel**
   ```bash
   vercel login
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the frontend directory with:
   ```
   VITE_API_BASE_URL=https://your-fly-app-name.fly.dev
   ```

4. **Deploy to Vercel**
   ```bash
   cd frontend
   vercel
   ```

### Option 2: Netlify

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Authenticate with Netlify**
   ```bash
   netlify login
   ```

3. **Configure Environment Variables**
   ```bash
   netlify env:set VITE_API_BASE_URL https://your-fly-app-name.fly.dev
   ```

4. **Deploy to Netlify**
   ```bash
   cd frontend
   netlify deploy --prod
   ```

### Option 3: AWS S3 + CloudFront

1. **Build the Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://your-bucket-name
   ```

3. **Configure S3 for Static Website Hosting**
   ```bash
   aws s3 website s3://your-bucket-name --index-document index.html --error-document index.html
   ```

4. **Upload Build Files**
   ```bash
   aws s3 sync dist/ s3://your-bucket-name --acl public-read
   ```

5. **Create CloudFront Distribution**
   Follow AWS documentation to create a CloudFront distribution pointing to your S3 bucket.

## API Keys Setup

### OpenAI API Key

1. Create an account at [OpenAI](https://platform.openai.com/)
2. Generate an API key from the dashboard
3. Add the key to your backend environment variables

### Google Video Intelligence API

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Video Intelligence API
3. Create a service account and download the JSON credentials
4. Add the credentials to your backend environment

### S3 Storage

1. Create an S3 bucket in AWS or use an S3-compatible service
2. Generate access and secret keys
3. Add the keys to your backend environment variables

## Continuous Integration/Deployment (CI/CD)

For automated deployments, consider setting up GitHub Actions:

1. Create `.github/workflows/deploy.yml` with:
   ```yaml
   name: Deploy

   on:
     push:
       branches: [main]

   jobs:
     deploy-backend:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: superfly/flyctl-actions/setup-flyctl@master
         - run: cd backend && flyctl deploy --remote-only
           env:
             FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

     deploy-frontend:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-node@v2
           with:
             node-version: '18'
         - run: cd frontend && npm ci
         - run: cd frontend && npm run build
         - uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./frontend/dist
   ```

2. Add the required secrets to your GitHub repository

## Monitoring and Maintenance

- Set up logging with Fly.io's built-in logging system
- Configure alerts for application errors
- Regularly update dependencies and security patches

## Troubleshooting

### Backend Issues

- Check Fly.io logs: `fly logs`
- Verify environment variables: `fly secrets list`
- SSH into the instance: `fly ssh console`

### Frontend Issues

- Check browser console for errors
- Verify API endpoint configuration
- Test API connectivity from the frontend

## Additional Resources

- [Fly.io Documentation](https://fly.io/docs/)
- [Vercel Documentation](https://vercel.com/docs)
- [Netlify Documentation](https://docs.netlify.com/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
