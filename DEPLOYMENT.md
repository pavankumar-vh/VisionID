# VisionID Deployment Guide

## Quick Start (Development)

### 1. Local Setup
```bash
# Clone repository
git clone https://github.com/pavankumar-vh/VisionID.git
cd VisionID

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn app.main:app --reload
```

### 2. Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access API: http://localhost:8000/docs
```

## Production Deployment

### Option 1: Docker (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- GPU (optional, for acceleration)

#### Steps
```bash
# 1. Build production image
docker-compose -f docker-compose.yml build

# 2. Start services
docker-compose up -d

# 3. Verify deployment
curl http://localhost:8000/ping

# 4. View logs
docker-compose logs -f visionid-api
```

#### With GPU Support
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Add GPU support to docker-compose.yml:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: 1
#           capabilities: [gpu]
```

### Option 2: Manual Deployment

#### Ubuntu/Debian Server
```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3.10 python3-pip python3-venv \
  libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgl1-mesa-glx

# 2. Clone and setup
git clone https://github.com/pavankumar-vh/VisionID.git
cd VisionID
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Update DATABASE_URL and other settings

# 4. Create systemd service
sudo nano /etc/systemd/system/visionid.service
```

**visionid.service:**
```ini
[Unit]
Description=VisionID Face Recognition API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/VisionID
Environment="PATH=/path/to/VisionID/venv/bin"
ExecStart=/path/to/VisionID/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 5. Start service
sudo systemctl daemon-reload
sudo systemctl enable visionid
sudo systemctl start visionid
sudo systemctl status visionid
```

### Option 3: Kubernetes Deployment

```yaml
# visionid-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visionid-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: visionid-api
  template:
    metadata:
      labels:
        app: visionid-api
    spec:
      containers:
      - name: visionid
        image: visionid:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: visionid-secrets
              key: database-url
        resources:
          limits:
            memory: "4Gi"
            cpu: "2"
          requests:
            memory: "2Gi"
            cpu: "1"
---
apiVersion: v1
kind: Service
metadata:
  name: visionid-service
spec:
  selector:
    app: visionid-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

```bash
# Deploy to Kubernetes
kubectl apply -f visionid-deployment.yaml
```

## Production Configuration

### 1. PostgreSQL Setup
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE visionid_db;
CREATE USER visionid_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE visionid_db TO visionid_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://visionid_user:secure_password@localhost:5432/visionid_db
```

### 2. Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/visionid
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/visionid /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

## Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/ping

# Container health
docker-compose ps
docker inspect visionid-api | grep -i health

# Service status
sudo systemctl status visionid
```

### Logs
```bash
# Docker logs
docker-compose logs -f visionid-api

# System service logs
sudo journalctl -u visionid -f

# Application logs
tail -f logs/visionid.log
```

## Performance Tuning

### 1. Worker Configuration
```bash
# Calculate optimal workers
workers = (2 * CPU_cores) + 1

# Update in docker-compose.yml or systemd service
--workers 4
```

### 2. Database Optimization
```sql
-- PostgreSQL tuning
-- Edit /etc/postgresql/15/main/postgresql.conf

shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
max_connections = 100
```

### 3. GPU Optimization
```python
# For multiple GPUs, set in .env
GPU_ID=0,1  # Use first two GPUs
```

## Backup & Recovery

### Database Backup
```bash
# Backup PostgreSQL
pg_dump -U visionid_user visionid_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U visionid_user visionid_db < backup_20240101.sql

# Docker volume backup
docker run --rm -v visionid_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Application Backup
```bash
# Backup embeddings and uploads
tar -czf visionid_data_$(date +%Y%m%d).tar.gz data/ uploads/
```

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Verify dependencies
pip list | grep insightface
pip install --upgrade insightface
```

**2. GPU Not Detected**
```bash
# Check CUDA
nvidia-smi

# Test GPU in container
docker run --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**3. Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U visionid_user -d visionid_db -h localhost
```

**4. Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **Database**: Use strong passwords, restrict network access
3. **API Keys**: Implement authentication for production
4. **HTTPS**: Always use SSL in production
5. **File Upload**: Validate and sanitize all uploads
6. **Rate Limiting**: Implement rate limiting for API endpoints

## Scaling

### Horizontal Scaling
```bash
# Docker Compose
docker-compose up --scale visionid-api=3

# Kubernetes
kubectl scale deployment visionid-api --replicas=5
```

### Load Balancing
Use Nginx or HAProxy for load balancing multiple instances.

## Support

For issues and questions:
- GitHub Issues: https://github.com/pavankumar-vh/VisionID/issues
- Documentation: http://localhost:8000/docs
