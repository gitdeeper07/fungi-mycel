# 🍄 FUNGI-MYCEL DEPLOYMENT GUIDE

This guide covers deployment options for the FUNGI-MYCEL framework, including the live dashboard, API services, documentation, and data repositories.

---

## Table of Contents

- [Quick Deployments](#quick-deployments)
  - [Netlify (Dashboard)](#netlify-dashboard)
  - [Hugging Face Spaces (Interactive)](#hugging-face-spaces-interactive)
  - [PyPI (Python Package)](#pypi-python-package)
  - [ReadTheDocs (Documentation)](#readthedocs-documentation)
- [Production Deployments](#production-deployments)
  - [Docker](#docker)
  - [Docker Compose](#docker-compose)
  - [Kubernetes](#kubernetes)
  - [Cloud Providers](#cloud-providers)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Security](#security)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Scaling](#scaling)

---

## Quick Deployments

### Netlify (Dashboard)

The FUNGI-MYCEL interactive dashboard is pre-configured for Netlify deployment.

#### Automatic Deployment

1. Connect your Git repository to Netlify
2. Use these settings:
   - Build command: `cd dashboard && npm run build` (if using Node) or leave empty
   - Publish directory: `dashboard/dist` or `dashboard`
   - Environment variables: none required

3. Or use the `netlify.toml` configuration:
```toml
[build]
  publish = "dashboard"

[build.environment]
  PYTHON_VERSION = "3.11"
  NODE_VERSION = "18"

[redirects]
  from = "/api/*"
  to = "https://your-api-domain.com/:splat"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
```

Manual Deployment

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dashboard
```

Live dashboard: https://fungi-mycel.netlify.app

---

Hugging Face Spaces (Interactive)

Deploy an interactive version with Streamlit for model demonstrations.

Using Git

```bash
# Create space at huggingface.co/new-space
# Choose Streamlit SDK

git clone https://huggingface.co/spaces/fungi-mycel/fungi-mycel
cp -r dashboard/streamlit/* fungi-mycel-space/
cd fungi-mycel-space

# Create README.md
cat > README.md << 'README'
---
title: FUNGI-MYCEL
emoji: 🍄
colorFrom: green
colorTo: brown
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# FUNGI-MYCEL Interactive Explorer

Explore mycelial network intelligence with real-time MNIS calculations.

**Dashboard:** https://fungi-mycel.netlify.app
**Documentation:** https://fungi-mycel.readthedocs.io
README

git add .
git commit -m "Initial FUNGI-MYCEL Space"
git push
```

Space URL: https://huggingface.co/spaces/fungi-mycel/fungi-mycel

---

PyPI (Python Package)

Deploy the core FUNGI-MYCEL package to PyPI.

Preparation

```bash
# Install build tools
pip install build twine wheel

# Update version in setup.py/pyproject.toml
# Version: 1.0.0

# Create distribution files
python -m build
```

Upload to TestPyPI

```bash
# Upload to test server first
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ fungi-mycel
```

Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Install
pip install fungi-mycel
```

PyPI package: https://pypi.org/project/fungi-mycel

---

ReadTheDocs (Documentation)

Deploy technical documentation to ReadTheDocs.

Configuration

1. Connect your Git repository to readthedocs.org
2. Use the .readthedocs.yaml configuration in this repository
3. Build documentation automatically on push

Manual Build

```bash
# Build locally
cd docs
make html

# The documentation will be available at:
# https://fungi-mycel.readthedocs.io
```

Documentation: https://fungi-mycel.readthedocs.io

---

Production Deployments

Docker

Build Image

```dockerfile
# Dockerfile
FROM python:3.10-slim

LABEL maintainer="gitdeeper@gmail.com"
LABEL version="1.0.0"
LABEL description="FUNGI-MYCEL - Mycelial Network Intelligence Framework"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FUNGI_MYCEL_HOME=/opt/fungi-mycel \
    FUNGI_MYCEL_CONFIG=/etc/fungi-mycel/config.yaml

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libhdf5-dev \
    libnetcdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m -u 1000 -s /bin/bash fungi && \
    mkdir -p /opt/fungi-mycel && \
    mkdir -p /etc/fungi-mycel && \
    mkdir -p /data/field && \
    mkdir -p /data/backup && \
    chown -R fungi:fungi /opt/fungi-mycel /etc/fungi-mycel /data

# Switch to user
USER fungi
WORKDIR /opt/fungi-mycel

# Install Python dependencies
COPY --chown=fungi:fungi requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=fungi:fungi . .

# Install package
RUN pip install --user -e .

# Expose ports
EXPOSE 8000 8501

# Default command
CMD ["fungi-mycel", "serve", "--all"]
```

Build and Run

```bash
# Build image
docker build -t fungi-mycel:1.0.0 .

# Run container
docker run -d \
  --name fungi-mycel-prod \
  -p 8000:8000 \
  -p 8501:8501 \
  -v /host/data:/data \
  -v /host/config:/etc/fungi-mycel \
  -e FUNGI_MYCEL_CONFIG=/etc/fungi-mycel/config.yaml \
  --restart unless-stopped \
  fungi-mycel:1.0.0

# Check logs
docker logs -f fungi-mycel-prod

# Execute commands in container
docker exec -it fungi-mycel-prod fungi-mycel doctor
```

---

Docker Compose (Full Stack)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: fungi-postgres
    environment:
      POSTGRES_DB: fungi_mycel
      POSTGRES_USER: fungi_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-change_me}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fungi_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fungi-network

  redis:
    image: redis:7-alpine
    container_name: fungi-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis_pass}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fungi-network

  api:
    build: .
    container_name: fungi-api
    command: fungi-mycel serve --api --host 0.0.0.0 --port 8000
    environment:
      FUNGI_MYCEL_CONFIG: /etc/fungi-mycel/config.yaml
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: fungi_mycel
      DB_USER: fungi_user
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    volumes:
      - ./config:/etc/fungi-mycel
      - ./data:/data
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - fungi-network
    restart: unless-stopped

  dashboard:
    build: .
    container_name: fungi-dashboard
    command: fungi-mycel serve --dashboard --host 0.0.0.0 --port 8501
    environment:
      FUNGI_MYCEL_CONFIG: /etc/fungi-mycel/config.yaml
      API_URL: http://api:8000
    volumes:
      - ./config:/etc/fungi-mycel
    ports:
      - "8501:8501"
    depends_on:
      - api
    networks:
      - fungi-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: fungi-nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./www:/var/www/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
      - dashboard
    networks:
      - fungi-network
    restart: unless-stopped

  backup:
    image: postgres:15-alpine
    container_name: fungi-backup
    command: |
      sh -c "
      apk add --no-cache aws-cli &&
      while true; do
        PGPASSWORD=$$DB_PASSWORD pg_dump -h postgres -U fungi_user fungi_mycel > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql &&
        echo "Backup completed at $$(date)" &&
        sleep 86400
      done"
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./backups:/backups
      - ~/.aws:/root/.aws:ro
    depends_on:
      - postgres
    networks:
      - fungi-network

networks:
  fungi-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

Deploy with Docker Compose

```bash
# Set environment variables
export DB_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)

# Create directories
mkdir -p config data backups ssl www

# Copy configuration
cp config/fungi_mycel.prod.yaml config/config.yaml

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Scale API (if needed)
docker-compose up -d --scale api=3

# Stop services
docker-compose down

# Full cleanup
docker-compose down -v
```

---

Kubernetes

Deploy FUNGI-MYCEL on Kubernetes clusters.

Deployment Configuration

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fungi-mycel-api
  namespace: fungi-mycel
  labels:
    app: fungi-mycel
    component: api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fungi-mycel
      component: api
  template:
    metadata:
      labels:
        app: fungi-mycel
        component: api
        version: v1
    spec:
      containers:
      - name: api
        image: gitlab.com/fungi-mycel/fungi-mycel:1.0.0
        command: ["fungi-mycel", "serve", "--api", "--host", "0.0.0.0", "--port", "8000"]
        ports:
        - containerPort: 8000
        env:
        - name: FUNGI_MYCEL_CONFIG
          value: /etc/fungi-mycel/config.yaml
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: fungi-secrets
              key: db_host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fungi-secrets
              key: db_password
        volumeMounts:
        - name: config
          mountPath: /etc/fungi-mycel
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: fungi-config
      - name: data
        persistentVolumeClaim:
          claimName: fungi-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: fungi-api-service
  namespace: fungi-mycel
spec:
  selector:
    app: fungi-mycel
    component: api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fungi-api-hpa
  namespace: fungi-mycel
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fungi-mycel-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace fungi-mycel

# Create secrets
kubectl create secret generic fungi-secrets \
  --namespace fungi-mycel \
  --from-literal=db_host=postgres-service \
  --from-literal=db_password=$(openssl rand -base64 32)

# Create configmap
kubectl create configmap fungi-config \
  --namespace fungi-mycel \
  --from-file=config.yaml=config/fungi_mycel.k8s.yaml

# Apply deployments
kubectl apply -f k8s/

# Check status
kubectl get all -n fungi-mycel

# Scale
kubectl scale deployment fungi-mycel-api --replicas=5 -n fungi-mycel

# Rolling update
kubectl set image deployment/fungi-mycel-api \
  api=gitlab.com/fungi-mycel/fungi-mycel:1.0.1 -n fungi-mycel
```

---

Cloud Providers

AWS Deployment

```bash
# Using AWS ECS
# Create ECR repository
aws ecr create-repository --repository-name fungi-mycel

# Build and push image
docker build -t fungi-mycel .
docker tag fungi-mycel:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/fungi-mycel:latest
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/fungi-mycel:latest

# Deploy using ECS Fargate
aws ecs create-cluster --cluster-name fungi-mycel
aws ecs register-task-definition --cli-input-json file://aws-task.json
aws ecs create-service --cluster fungi-mycel --service-name fungi-api --task-definition fungi-mycel:1 --desired-count 2
```

Google Cloud Platform

```bash
# Using GCP Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/fungi-mycel
gcloud run deploy fungi-mycel \
  --image gcr.io/PROJECT_ID/fungi-mycel \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

Azure Deployment

```bash
# Using Azure Container Instances
az container create \
  --resource-group fungi-group \
  --name fungi-mycel \
  --image gitlab.com/fungi-mycel/fungi-mycel:latest \
  --ports 8000 8501 \
  --cpu 2 \
  --memory 4 \
  --environment-variables FUNGI_MYCEL_CONFIG=/etc/fungi-mycel/config.yaml \
  --azure-file-volume-account-name storageaccount \
  --azure-file-volume-share-name fungi-config \
  --azure-file-volume-mount-path /etc/fungi-mycel
```

---

Database Setup

PostgreSQL Schema

```sql
-- init-db.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Sites table
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_code VARCHAR(20) UNIQUE NOT NULL,
    site_name VARCHAR(100) NOT NULL,
    biome_type VARCHAR(50) NOT NULL,
    country VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    elevation_m INTEGER,
    established_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MNU (Mycelial Network Units) table
CREATE TABLE mnus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID REFERENCES sites(id),
    mnu_code VARCHAR(20) UNIQUE NOT NULL,
    sampling_date DATE NOT NULL,
    depth_cm INTEGER,
    soil_type VARCHAR(50),
    dominant_fungi TEXT[],
    host_trees TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parameters table
CREATE TABLE parameters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mnu_id UUID REFERENCES mnus(id),
    eta_nw DECIMAL(5,2),  -- Natural Weathering Efficiency
    rho_e DECIMAL(5,2),    -- Bioelectrical Pulse Density
    grad_c DECIMAL(5,2),   -- Chemotropic Navigation
    ser DECIMAL(5,2),      -- Symbiotic Exchange Ratio
    k_topo DECIMAL(5,2),   -- Topological Expansion
    abi DECIMAL(5,2),      -- Biodiversity Amplification
    bfs DECIMAL(5,2),      -- Biological Field Stability
    e_a DECIMAL(5,2),      -- Adaptive Resilience
    mnis DECIMAL(5,2),      -- Composite Score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bioelectrical recordings
CREATE TABLE bioelectrical (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mnu_id UUID REFERENCES mnus(id),
    recording_start TIMESTAMP,
    recording_end TIMESTAMP,
    sampling_rate_hz INTEGER,
    electrode_count INTEGER,
    data_file TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_parameters_mnis ON parameters(mnis);
CREATE INDEX idx_parameters_rho_e ON parameters(rho_e);
CREATE INDEX idx_mnus_site_id ON mnus(site_id);
CREATE INDEX idx_mnus_sampling_date ON mnus(sampling_date);
```

---

Configuration

Production Configuration

```yaml
# config/fungi_mycel.prod.yaml
# FUNGI-MYCEL Production Configuration

version: 1.0
environment: production

server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  timeout: 120
  ssl_cert: /etc/ssl/certs/fungi-mycel.crt
  ssl_key: /etc/ssl/private/fungi-mycel.key

database:
  host: postgres-service
  port: 5432
  name: fungi_mycel
  user: fungi_user
  password: ${DB_PASSWORD}
  pool_size: 20
  max_overflow: 40
  pool_timeout: 30

redis:
  host: redis-service
  port: 6379
  password: ${REDIS_PASSWORD}
  db: 0
  socket_timeout: 5

logging:
  level: WARNING
  format: json
  file: /var/log/fungi-mycel/app.log
  max_size: 100MB
  backup_count: 10

monitoring:
  metrics_enabled: true
  metrics_port: 9090
  sentry_dsn: ${SENTRY_DSN}
  new_relic_license: ${NEW_RELIC_LICENSE}

security:
  jwt_secret: ${JWT_SECRET}
  jwt_expiry_hours: 24
  rate_limit: 100/minute
  cors_origins:
    - https://fungi-mycel.netlify.app
    - https://fungi-mycel.readthedocs.io
  allowed_hosts:
    - api.fungi-mycel.org
    - dashboard.fungi-mycel.org

field_data:
  upload_dir: /data/uploads
  max_file_size: 1GB
  allowed_formats:
    - .npy
    - .csv
    - .tif
    - .fasta
  auto_process: true
  backup_enabled: true
  backup_bucket: s3://fungi-mycel-backups

email:
  smtp_host: smtp.gmail.com
  smtp_port: 587
  smtp_user: notifications@fungi-mycel.org
  smtp_password: ${SMTP_PASSWORD}
  alerts_enabled: true
  alert_recipients:
    - gitdeeper@gmail.com
    - alerts@fungi-mycel.org
```

---

Security

SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.fungi-mycel.org;

    ssl_certificate /etc/nginx/ssl/fungi-mycel.crt;
    ssl_certificate_key /etc/nginx/ssl/fungi-mycel.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://fungi-api-service:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name api.fungi-mycel.org;
    return 301 https://$server_name$request_uri;
}
```

Environment Variables

```bash
# .env.production
DB_PASSWORD=super_secure_password_2026
REDIS_PASSWORD=another_secure_password
JWT_SECRET=your_jwt_secret_key_here
SENTRY_DSN=https://key@sentry.io/project
SMTP_PASSWORD=email_password
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
NEW_RELIC_LICENSE=your_license_key
```

---

Monitoring

Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'fungi-mycel'
    static_configs:
      - targets: ['api:8000', 'dashboard:8501']
    metrics_path: /metrics
    scrape_interval: 15s
```

Grafana Dashboard

Import the FUNGI-MYCEL dashboard template (monitoring/grafana-dashboard.json) to visualize:

· MNIS scores across sites
· ρ_e activity in real-time
· Parameter correlations
· Early warning alerts
· System health metrics

---

Backup & Recovery

Automated Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
S3_BUCKET="s3://fungi-mycel-backups"

# Database backup
pg_dump -h postgres -U fungi_user fungi_mycel | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Field data backup
tar -czf $BACKUP_DIR/field_data_$DATE.tar.gz /data/field

# Configuration backup
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/fungi-mycel

# Upload to S3
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz $S3_BUCKET/database/
aws s3 cp $BACKUP_DIR/field_data_$DATE.tar.gz $S3_BUCKET/field/
aws s3 cp $BACKUP_DIR/config_$DATE.tar.gz $S3_BUCKET/config/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Recovery Procedure

```bash
# Restore database
gunzip -c backup.sql.gz | psql -h postgres -U fungi_user fungi_mycel

# Restore field data
tar -xzf field_data.tar.gz -C /data/field

# Restore config
tar -xzf config.tar.gz -C /etc/fungi-mycel
```

---

Scaling

Horizontal Scaling

· API servers: Scale based on CPU/Memory metrics
· Dashboard: Multiple instances behind load balancer
· Database: Read replicas for queries
· Redis: Cluster mode for caching

Vertical Scaling

· Increase resources for ML model serving
· Optimize database indexes
· Implement connection pooling
· Use CDN for static assets

Performance Tuning

```python
# performance.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Optimize MNIS calculation
executor = ThreadPoolExecutor(max_workers=4)

async def batch_process_mnus(mnu_ids):
    """Process multiple MNUs in parallel."""
    loop = asyncio.get_event_loop()
    tasks = []
    for mnu_id in mnu_ids:
        task = loop.run_in_executor(executor, calculate_mnis, mnu_id)
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_biome_reference(biome_type):
    """Cache biome reference distributions."""
    return load_biome_data(biome_type)
```

---

Support

For deployment assistance:

· Documentation: https://fungi-mycel.readthedocs.io
· Dashboard: https://fungi-mycel.netlify.app
· Issues: https://gitlab.com/gitdeeper07/fungi-mycel/-/issues
· Email: deploy@fungi-mycel.org
· Principal Investigator: gitdeeper@gmail.com

---

Quick Reference

```bash
# Netlify Dashboard
https://fungi-mycel.netlify.app

# PyPI Package
pip install fungi-mycel

# Docker
docker pull gitlab.com/fungi-mycel/fungi-mycel:latest

# Documentation
https://fungi-mycel.readthedocs.io

# Source Code
https://gitlab.com/gitdeeper07/fungi-mycel
https://github.com/gitdeeper07/fungi-mycel
```

---

🍄 The forest speaks. FUNGI-MYCEL translates.

DOI: 10.14293/FUNGI-MYCEL.2026.001
