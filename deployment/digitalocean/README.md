# DigitalOcean Deployment Guide for Short-Form Video Accelerator

This guide provides instructions for deploying the Short-Form Video Accelerator application to DigitalOcean.

## Prerequisites

- [DigitalOcean](https://www.digitalocean.com/) account
- [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) CLI tool installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) installed
- Docker installed locally

## Frontend Deployment

### 1. Build the Frontend

```bash
cd /path/to/short-form-video-accelerator/frontend
npm install
npm run build
```

This will create a `dist` directory with the built frontend assets.

### 2. Create a ConfigMap for Frontend Files

```bash
# Create a ConfigMap from the dist directory
kubectl create configmap short-form-video-accelerator-frontend-files --from-file=dist/ --dry-run=client -o yaml > frontend-files-configmap.yaml
kubectl apply -f frontend-files-configmap.yaml
```

### 3. Create a ConfigMap for Nginx Configuration

Create a file named `nginx-config.yaml` with the following content:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: short-form-video-accelerator-nginx-config
data:
  default.conf: |
    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }
    }
```

Apply the configuration:

```bash
kubectl apply -f nginx-config.yaml
```

### 4. Deploy the Frontend

Apply the deployment configuration:

```bash
kubectl apply -f app.yaml
```

### 5. Get the Frontend URL

```bash
kubectl get service short-form-video-accelerator-frontend
```

Note the external IP address provided by DigitalOcean. This is your frontend URL.

## Backend Deployment

### 1. Build and Push the Backend Docker Image

```bash
cd /path/to/short-form-video-accelerator/backend

# Build the Docker image
docker build -t registry.digitalocean.com/your-registry/short-form-video-accelerator-backend:latest .

# Push to DigitalOcean Container Registry
docker push registry.digitalocean.com/your-registry/short-form-video-accelerator-backend:latest
```

### 2. Create Kubernetes Secrets for Environment Variables

```bash
kubectl create secret generic short-form-video-accelerator-backend-env \
  --from-literal=DATABASE_URL=sqlite:///./app.db \
  --from-literal=SECRET_KEY=your-secret-key \
  --from-literal=OPENAI_API_KEY=your-openai-api-key \
  --from-literal=S3_ENDPOINT=your-s3-endpoint \
  --from-literal=S3_ACCESS_KEY=your-s3-access-key \
  --from-literal=S3_SECRET_KEY=your-s3-secret-key \
  --from-literal=S3_BUCKET_NAME=your-s3-bucket-name \
  --from-literal=S3_REGION=your-s3-region
```

### 3. Create a Kubernetes Secret for Google Credentials

```bash
kubectl create secret generic google-credentials --from-file=credentials.json=/path/to/google-credentials.json
```

### 4. Create Backend Deployment Configuration

Create a file named `backend.yaml` with the following content:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: short-form-video-accelerator-backend
  labels:
    app: short-form-video-accelerator-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: short-form-video-accelerator-backend
  template:
    metadata:
      labels:
        app: short-form-video-accelerator-backend
    spec:
      containers:
      - name: backend
        image: registry.digitalocean.com/your-registry/short-form-video-accelerator-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: short-form-video-accelerator-backend-env
        volumeMounts:
        - name: google-credentials
          mountPath: /app/google-credentials.json
          subPath: credentials.json
      volumes:
      - name: google-credentials
        secret:
          secretName: google-credentials
---
apiVersion: v1
kind: Service
metadata:
  name: short-form-video-accelerator-backend
spec:
  selector:
    app: short-form-video-accelerator-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Apply the configuration:

```bash
kubectl apply -f backend.yaml
```

### 5. Get the Backend URL

```bash
kubectl get service short-form-video-accelerator-backend
```

Note the external IP address. This is your backend URL.

## Update Frontend Configuration

After deploying the backend, update the frontend configuration to use the backend URL:

1. Update the `.env` file in the frontend directory:

```
VITE_API_URL=http://your-backend-external-ip
```

2. Rebuild and redeploy the frontend following steps 1-4 in the Frontend Deployment section.

## Monitoring and Maintenance

### View Logs

```bash
# View backend logs
kubectl logs -f deployment/short-form-video-accelerator-backend

# View frontend logs
kubectl logs -f deployment/short-form-video-accelerator-frontend
```

### Scale the Application

```bash
# Scale backend
kubectl scale deployment short-form-video-accelerator-backend --replicas=3

# Scale frontend
kubectl scale deployment short-form-video-accelerator-frontend --replicas=3
```

### Update the Application

To update the application, rebuild the Docker images with new tags, push them to the registry, and update the deployments to use the new images.

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods
```

### Describe a Pod for Detailed Information

```bash
kubectl describe pod pod-name
```

### Access a Pod Shell

```bash
kubectl exec -it pod-name -- /bin/sh
```
