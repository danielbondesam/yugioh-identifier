# Docker Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker installed: https://docs.docker.com/get-docker/
- Docker Compose (usually included with Docker Desktop)

### Build and Run

#### Option 1: Using docker-compose (Recommended)

```bash
cd c:\workflow\projects\yugioh-identifier

# Build and start both services
docker-compose up --build

# In browser, visit:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - Swagger Docs: http://localhost:8000/docs
```

Stop services:
```bash
docker-compose down

# Remove volumes too (cleans up cache)
docker-compose down -v
```

#### Option 2: Build Individual Containers

**Backend:**
```bash
cd backend

# Build image
docker build -t yugioh-identifier-backend .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/cache:/app/cache \
  yugioh-identifier-backend
```

**Frontend:**
```bash
cd frontend

# Build image
docker build -t yugioh-identifier-frontend .

# Run container
docker run -p 3000:3000 \
  -e REACT_APP_BACKEND_URL=http://localhost:8000 \
  yugioh-identifier-frontend
```

## Configuration

### Environment Variables

Backend (docker-compose.yml):
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - TESSERACT_PATH=/usr/bin/tesseract
  - MIN_CONFIDENCE=0.75
  - FUZZY_MATCH_THRESHOLD=80
  - CACHE_EXPIRY_HOURS=24
```

Frontend (docker-compose.yml):
```yaml
environment:
  - REACT_APP_BACKEND_URL=http://backend:8000
```

### Persistent Cache

The backend cache is mounted as a volume:
```yaml
volumes:
  - ./backend/cache:/app/cache
```

This keeps the card database between container restarts.

## Troubleshooting

### Container won't start

Check logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend
```

### Port already in use

Change ports in docker-compose.yml:
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Changed from 8000
  
  frontend:
    ports:
      - "3001:3000"  # Changed from 3000
```

Then access at http://localhost:3001

### Backend can't reach Tesseract

Error: "Tesseract is not installed or not in PATH"

The Dockerfile installs tesseract via `apt-get`. If issue persists:

```bash
# Rebuild without cache
docker-compose build --no-cache backend

# Restart
docker-compose up backend
```

### Frontend can't reach backend

Set correct backend URL in docker-compose.yml:

```yaml
# Within same docker network (default for compose)
REACT_APP_BACKEND_URL=http://backend:8000

# From host machine
REACT_APP_BACKEND_URL=http://localhost:8000
```

## Production Deployment

### Using Kubernetes

Create deployment manifests (advanced):
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: yugioh-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    # ... pod spec
```

### Using Cloud Platforms

**AWS (EC2 + ECR):**
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag yugioh-identifier-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/yugioh-identifier-backend:latest

docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/yugioh-identifier-backend:latest
```

**Google Cloud (Cloud Run):**
```bash
gcloud builds submit --tag gcr.io/my-project/yugioh-backend ./backend

gcloud run deploy yugioh-backend \
  --image gcr.io/my-project/yugioh-backend \
  --platform managed
```

**Azure (Container Registry):**
```bash
az acr build --registry myregistry --image yugioh-backend:latest ./backend

az container create \
  --resource-group mygroup \
  --name yugioh-backend \
  --image myregistry.azurecr.io/yugioh-backend:latest
```

### Nginx Reverse Proxy

For production, use Nginx to serve frontend and proxy backend:

```nginx
server {
    listen 80;
    server_name example.com;

    # Frontend (React build)
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }

    # Backend API
    location /api {
        rewrite ^/api(.*) $1 break;
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
    }
}
```

## Monitoring

### Health Checks

Docker Compose includes automatic health checks:
```bash
docker-compose ps
# Shows status of each service
```

### Container Logs

```bash
# View logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Get last 100 lines
docker-compose logs --tail=100
```

### Resource Usage

```bash
docker stats
# Shows CPU, memory, network usage
```

## Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Complete cleanup (be careful!)
docker system prune -a
```

## Advanced Configuration

### Build Arguments

Pass build arguments:
```bash
docker build --build-arg PYTHON_VERSION=3.11 ./backend
```

### Multi-stage Build (Optimize)

Frontend optimized build:
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
```

### Docker Secrets (Production)

```bash
echo "my_secret_value" | docker secret create my_secret -

# Use in compose:
docker stack deploy -c docker-compose-secrets.yml myapp
```

---

For more info: https://docs.docker.com/
