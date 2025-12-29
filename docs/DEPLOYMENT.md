# Deployment Guide

This guide covers different deployment options for the Financial RAG Assistant.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
nano .env  # Add your OPENAI_API_KEY

# Run development server
python main.py
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

**Backend:**
```bash
cd backend
docker build -t financial-rag-backend .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  financial-rag-backend
```

**Frontend:**
```bash
cd frontend
docker build -t financial-rag-frontend .
docker run -p 3000:3000 financial-rag-frontend
```

---

## Production Deployment

### Backend (FastAPI)

#### Option 1: Gunicorn + Uvicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

#### Option 2: Uvicorn with systemd

Create `/etc/systemd/system/financial-rag.service`:

```ini
[Unit]
Description=Financial RAG Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/financial-rag/backend
Environment="OPENAI_API_KEY=your_key"
ExecStart=/opt/financial-rag/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable financial-rag
sudo systemctl start financial-rag
```

### Frontend (React)

#### Build for Production

```bash
cd frontend

# Build optimized bundle
npm run build

# Output in dist/ directory
```

#### Serve with Nginx

Create `/etc/nginx/sites-available/financial-rag`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        root /opt/financial-rag/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/financial-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04
   - Instance Type: t3.medium (minimum)
   - Security Group: Allow ports 22, 80, 443

2. **Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Nginx
sudo apt install nginx -y
```

3. **Deploy Application**
```bash
# Clone repository
git clone your-repo-url /opt/financial-rag
cd /opt/financial-rag

# Setup backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
npm run build
```

4. **Configure systemd and Nginx** (see Production Deployment above)

#### Using ECS (Container Service)

1. Push Docker images to ECR
2. Create ECS cluster
3. Define task definitions
4. Create services
5. Configure load balancer

### Vercel Deployment (Frontend Only)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

Configure environment variable:
- `VITE_API_URL`: Your backend URL

### Railway Deployment (Full Stack)

1. Create account at railway.app
2. Connect GitHub repository
3. Configure services:
   - **Backend**: Auto-detect Python, add `OPENAI_API_KEY`
   - **Frontend**: Auto-detect Node.js, add `VITE_API_URL`

---

## Environment Variables

### Backend (.env)

```env
OPENAI_API_KEY=sk-...
HOST=0.0.0.0
PORT=8000
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

### Frontend (.env)

```env
VITE_API_URL=https://api.yourdomain.com
```

---

## Performance Optimization

### Backend

1. **Enable caching**
   - Use Redis for distributed caching
   - Configure cache TTL based on query patterns

2. **Database optimization**
   - Use persistent FAISS index on fast SSD
   - Implement index sharding for large datasets

3. **Async processing**
   - Use Celery for document processing
   - Implement job queues for uploads

### Frontend

1. **Build optimization**
   ```bash
   npm run build -- --mode production
   ```

2. **CDN deployment**
   - Deploy static assets to CDN
   - Enable gzip compression

3. **Lazy loading**
   - Implement code splitting
   - Lazy load components

---

## Monitoring

### Application Monitoring

Add monitoring endpoints:

```python
from prometheus_client import Counter, Histogram

query_counter = Counter('queries_total', 'Total queries')
query_duration = Histogram('query_duration_seconds', 'Query duration')
```

### Infrastructure Monitoring

- **Metrics**: Prometheus + Grafana
- **Logs**: ELK Stack or CloudWatch
- **Uptime**: UptimeRobot or Pingdom

---

## Security Checklist

- [ ] Set strong API keys
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Sanitize file uploads
- [ ] Enable security headers
- [ ] Regular security updates
- [ ] Backup vector database
- [ ] Monitor for anomalies

---

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
```bash
pip install -r requirements.txt --force-reinstall
```

**FAISS index corruption:**
```bash
rm -rf backend/data/*.bin
# Re-upload documents
```

### Frontend Issues

**Build fails:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

**API connection refused:**
- Check VITE_API_URL in .env
- Verify backend is running
- Check CORS configuration

---

## Backup and Recovery

### Backup Vector Database

```bash
# Backup
tar -czf backup_$(date +%Y%m%d).tar.gz backend/data/

# Restore
tar -xzf backup_20240115.tar.gz -C /opt/financial-rag/
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * cd /opt/financial-rag && tar -czf backup_$(date +\%Y\%m\%d).tar.gz backend/data/
```

---

## Scaling Strategies

1. **Horizontal Scaling**
   - Load balance multiple backend instances
   - Shared vector database (Redis/PostgreSQL with pgvector)

2. **Vertical Scaling**
   - Increase RAM for larger vector indices
   - Use GPU for faster embeddings

3. **Caching Layer**
   - Redis for query caching
   - CDN for static assets

---

For more help, consult the [README.md](../README.md) or open an issue.
