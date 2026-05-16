# 🚀 Deployment Guide - Compass AI

Complete guide for deploying the IBM Bob Mentor System to production.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Monitoring & Logging](#monitoring--logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.12+**
- **pip** (Python package manager)
- **Git**
- **IBM WatsonX Account** with API credentials

### Optional (for production)

- **Docker** & Docker Compose
- **Nginx** (reverse proxy)
- **Supervisor** or **systemd** (process management)
- **PostgreSQL** (if adding database features)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Team-AVON-Project-for-IBM-BOB-DEV-DAY
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

Create `.env` file in project root:

```env
# IBM WatsonX Configuration
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Features
ENABLE_DEPENDENCY_SCORES=true
MAX_CONTEXT_FILES=10
MAX_RESPONSE_TOKENS=500
```

---

## Local Development

### Start Development Server

```bash
# With auto-reload
uvicorn bob_core.main:app --reload --port 8000

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Run Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=bob_core --cov-report=html

# Specific test file
python -m pytest tests/test_integration.py -v
```

### Code Quality Checks

```bash
# Format code
black bob_core/ tests/

# Lint
flake8 bob_core/ tests/

# Type checking
mypy bob_core/
```

---

## Production Deployment

### Option 1: Direct Python Deployment

#### 1. Install Production Dependencies

```bash
pip install gunicorn uvicorn[standard]
```

#### 2. Create Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/compass-ai/access.log'
errorlog = '/var/log/compass-ai/error.log'
loglevel = os.getenv('LOG_LEVEL', 'info')

# Process naming
proc_name = 'compass-ai'

# Server mechanics
daemon = False
pidfile = '/var/run/compass-ai.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'
```

#### 3. Start Production Server

```bash
# Create log directory
sudo mkdir -p /var/log/compass-ai
sudo chown $USER:$USER /var/log/compass-ai

# Start with Gunicorn
gunicorn bob_core.main:app -c gunicorn_config.py
```

#### 4. Setup Systemd Service

Create `/etc/systemd/system/compass-ai.service`:

```ini
[Unit]
Description=Compass AI - IBM Bob Mentor System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/compass-ai
Environment="PATH=/opt/compass-ai/venv/bin"
EnvironmentFile=/opt/compass-ai/.env
ExecStart=/opt/compass-ai/venv/bin/gunicorn bob_core.main:app -c gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable compass-ai
sudo systemctl start compass-ai
sudo systemctl status compass-ai
```

### Option 2: Nginx Reverse Proxy

#### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

#### 2. Configure Nginx

Create `/etc/nginx/sites-available/compass-ai`:

```nginx
upstream compass_ai {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logging
    access_log /var/log/nginx/compass-ai-access.log;
    error_log /var/log/nginx/compass-ai-error.log;

    # Max upload size
    client_max_body_size 10M;

    # Proxy settings
    location / {
        proxy_pass http://compass_ai;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://compass_ai;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files (if any)
    location /static {
        alias /opt/compass-ai/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/compass-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Docker Deployment

### 1. Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bob_core/ ./bob_core/
COPY engine/ ./engine/
COPY tests/ ./tests/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start application
CMD ["uvicorn", "bob_core.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  compass-ai:
    build: .
    container_name: compass-ai
    ports:
      - "8000:8000"
    environment:
      - WATSONX_API_KEY=${WATSONX_API_KEY}
      - WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID}
      - WATSONX_URL=${WATSONX_URL}
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - compass-network

  nginx:
    image: nginx:alpine
    container_name: compass-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - compass-ai
    restart: unless-stopped
    networks:
      - compass-network

networks:
  compass-network:
    driver: bridge
```

### 3. Build and Run

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Monitoring & Logging

### Application Logging

Configure in `bob_core/main.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/compass-ai.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Health Monitoring

Use the `/health` endpoint:

```bash
# Check health
curl http://localhost:8000/health

# Expected response
{"status": "ok", "service": "Compass AI"}
```

### Metrics Collection

Consider adding:

- **Prometheus** for metrics
- **Grafana** for visualization
- **Sentry** for error tracking

---

## Security Considerations

### 1. API Key Management

- Never commit `.env` files
- Use environment variables
- Rotate keys regularly
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)

### 2. CORS Configuration

Update in `bob_core/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

Add rate limiting middleware:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/ask")
@limiter.limit("10/minute")
async def ask_mentor(request: Request, payload: AskRequest):
    # ... endpoint logic
```

### 4. Input Validation

- All inputs validated with Pydantic
- Sanitize file paths
- Limit request sizes
- Validate repository paths

---

## Troubleshooting

### Common Issues

#### 1. WatsonX API Errors

```bash
# Check API key
echo $WATSONX_API_KEY

# Test connection
curl -X POST $WATSONX_URL/ml/v1/text/generation \
  -H "Authorization: Bearer $WATSONX_API_KEY"
```

#### 2. Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### 3. Permission Errors

```bash
# Fix log directory permissions
sudo chown -R $USER:$USER /var/log/compass-ai

# Fix application directory
sudo chown -R www-data:www-data /opt/compass-ai
```

#### 4. Memory Issues

```bash
# Check memory usage
free -h

# Reduce workers in gunicorn_config.py
workers = 2
```

### Logs Location

- **Application**: `/var/log/compass-ai/`
- **Nginx**: `/var/log/nginx/`
- **Systemd**: `journalctl -u compass-ai -f`
- **Docker**: `docker-compose logs -f`

---

## Performance Optimization

### 1. Caching

Add Redis for caching:

```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=100)
def get_file_context(file_path: str):
    # Cache file context
    pass
```

### 2. Database Connection Pooling

If using database:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 3. Async Operations

Ensure all I/O operations are async:

```python
import aiofiles

async def read_file_async(path: str) -> str:
    async with aiofiles.open(path, 'r') as f:
        return await f.read()
```

---

## Backup & Recovery

### Backup Strategy

```bash
# Backup configuration
tar -czf compass-ai-config-$(date +%Y%m%d).tar.gz .env gunicorn_config.py

# Backup logs
tar -czf compass-ai-logs-$(date +%Y%m%d).tar.gz /var/log/compass-ai/
```

### Recovery

```bash
# Restore configuration
tar -xzf compass-ai-config-YYYYMMDD.tar.gz

# Restart service
sudo systemctl restart compass-ai
```

---

## Scaling

### Horizontal Scaling

Use load balancer (e.g., HAProxy, AWS ELB):

```
                    ┌─────────────┐
                    │Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │Instance1│       │Instance2│       │Instance3│
   └─────────┘       └─────────┘       └─────────┘
```

### Vertical Scaling

- Increase worker count
- Add more CPU/RAM
- Optimize database queries

---

## Support

For issues or questions:

- Check [Troubleshooting](#troubleshooting)
- Review logs
- Contact Team AVON

---

**Last Updated**: 2026-05-16  
**Version**: 1.0.0