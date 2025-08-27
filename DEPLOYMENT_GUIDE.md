# Production Deployment Guide
## J.K. OVERSEAS PVT.LTD. Management System

## 🏗️ Architecture Overview

This guide covers deploying both the Django REST API backend and React frontend to production environments.

### System Components
- **Backend**: Django REST API with PostgreSQL
- **Frontend**: React SPA served via CDN/Nginx
- **Authentication**: JWT tokens with refresh mechanism
- **File Storage**: AWS S3 or local storage
- **Caching**: Redis for session and query caching

## 🚀 Backend Deployment (Django API)

### 1. Environment Setup

#### Production Settings
Create `company_management/settings_production.py`:

```python
from .settings import *
import os
from pathlib import Path

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AWS S3 Configuration (Optional)
if os.environ.get('USE_S3') == 'True':
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS for Production
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/app.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

#### Environment Variables
Create `.env` file:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database
DB_NAME=jk_overseas_db
DB_USER=jk_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# AWS S3 (Optional)
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=jk-overseas-storage
AWS_S3_REGION_NAME=us-east-1

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 2. Server Setup (Ubuntu/Debian)

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and PostgreSQL
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx -y

# Install Redis (for caching)
sudo apt install redis-server -y
```

#### Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql

CREATE DATABASE jk_overseas_db;
CREATE USER jk_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE jk_overseas_db TO jk_user;
ALTER USER jk_user CREATEDB;
\q
```

#### Application Setup
```bash
# Create application directory
sudo mkdir -p /var/www/jk-overseas
sudo chown $USER:$USER /var/www/jk-overseas

# Clone repository
cd /var/www/jk-overseas
git clone your-repository-url .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Set up environment variables
cp .env.example .env
# Edit .env with production values

# Run migrations
python manage.py migrate --settings=company_management.settings_production

# Create superuser
python manage.py createsuperuser --settings=company_management.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=company_management.settings_production
```

### 3. Gunicorn Configuration

Create `/var/www/jk-overseas/gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "www-data"
group = "www-data"
tmp_upload_dir = None
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

#### Systemd Service
Create `/etc/systemd/system/jk-overseas.service`:

```ini
[Unit]
Description=J.K. OVERSEAS Django API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=jk-overseas
WorkingDirectory=/var/www/jk-overseas
Environment=DJANGO_SETTINGS_MODULE=company_management.settings_production
ExecStart=/var/www/jk-overseas/venv/bin/gunicorn company_management.wsgi:application -c /var/www/jk-overseas/gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable jk-overseas
sudo systemctl start jk-overseas
sudo systemctl status jk-overseas
```

### 4. Nginx Configuration

Create `/etc/nginx/sites-available/jk-overseas`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # API Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static Files
    location /static/ {
        alias /var/www/jk-overseas/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/jk-overseas/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/jk-overseas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🌐 Frontend Deployment (React)

### 1. Build Process

#### Local Build
```bash
cd frontend

# Install dependencies
npm ci

# Create production build
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1 npm run build

# Test build locally
npx serve -s build
```

#### Build Optimization
Create `frontend/.env.production`:

```bash
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1
REACT_APP_COMPANY_NAME=J.K. OVERSEAS PVT.LTD.
GENERATE_SOURCEMAP=false
```

### 2. Static Hosting Options

#### Option A: Nginx Static Hosting
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (same as API)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /var/www/jk-overseas-frontend/build;
    index index.html;

    # React Router Support
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static Assets Caching
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

#### Option B: AWS S3 + CloudFront
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Create S3 bucket
aws s3 mb s3://jk-overseas-frontend

# Upload build files
aws s3 sync build/ s3://jk-overseas-frontend --delete

# Configure bucket for static website hosting
aws s3 website s3://jk-overseas-frontend --index-document index.html --error-document index.html
```

#### Option C: Netlify Deployment
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod --dir=build
```

### 3. CI/CD Pipeline

#### GitHub Actions Example
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/jk-overseas
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate --settings=company_management.settings_production
            python manage.py collectstatic --noinput --settings=company_management.settings_production
            sudo systemctl restart jk-overseas

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install and build
        run: |
          cd frontend
          npm ci
          npm run build
        env:
          REACT_APP_API_BASE_URL: https://api.yourdomain.com/api/v1
      
      - name: Deploy to S3
        run: |
          aws s3 sync frontend/build/ s3://jk-overseas-frontend --delete
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 🔒 SSL Certificate Setup

### Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### 1. Application Monitoring

#### Django Logging
```python
# settings_production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
}
```

#### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor services
sudo systemctl status jk-overseas
sudo systemctl status nginx
sudo systemctl status postgresql

# Check logs
sudo journalctl -u jk-overseas -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Performance Monitoring

#### Database Performance
```sql
-- Monitor slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Monitor database connections
SELECT count(*) FROM pg_stat_activity;
```

#### Application Performance
```python
# Add to Django settings
INSTALLED_APPS += ['django_extensions']

# Use Django Debug Toolbar in development
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

## 🔧 Maintenance Tasks

### Regular Maintenance
```bash
#!/bin/bash
# maintenance.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Backup database
pg_dump jk_overseas_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Clean old log files
find /var/log -name "*.log" -mtime +30 -delete

# Restart services
sudo systemctl restart jk-overseas
sudo systemctl restart nginx

# Check disk space
df -h

# Check memory usage
free -h
```

### Database Backup Strategy
```bash
#!/bin/bash
# backup.sh

DB_NAME="jk_overseas_db"
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://jk-overseas-backups/
```

## 🚨 Troubleshooting

### Common Issues

#### 1. 502 Bad Gateway
```bash
# Check Gunicorn status
sudo systemctl status jk-overseas

# Check Gunicorn logs
sudo journalctl -u jk-overseas -f

# Check if port is listening
sudo netstat -tlnp | grep :8000
```

#### 2. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t

# Check file permissions
ls -la /var/www/jk-overseas/staticfiles/
```

#### 3. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
psql -h localhost -U jk_user -d jk_overseas_db

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 4. CORS Issues
```python
# Update Django settings
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Or for development
CORS_ALLOW_ALL_ORIGINS = True  # Only for development!
```

## 📈 Performance Optimization

### Backend Optimization
```python
# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        },
    }
}

# Redis caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Frontend Optimization
```javascript
// Code splitting
const UserManagement = React.lazy(() => import('./components/UserManagement'));

// Service worker for caching
// In public/sw.js
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    // Cache API responses
    event.respondWith(
      caches.open('api-cache').then(cache => {
        return cache.match(event.request).then(response => {
          return response || fetch(event.request).then(fetchResponse => {
            cache.put(event.request, fetchResponse.clone());
            return fetchResponse;
          });
        });
      })
    );
  }
});
```

## 🔐 Security Checklist

### Backend Security
- [ ] Use HTTPS everywhere
- [ ] Set secure headers (HSTS, CSP, etc.)
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] API rate limiting
- [ ] Input validation and sanitization
- [ ] Secure file upload handling
- [ ] Regular security audits

### Frontend Security
- [ ] Content Security Policy
- [ ] Secure token storage
- [ ] XSS protection
- [ ] Dependency vulnerability scanning
- [ ] Secure build process
- [ ] Environment variable protection

---

This deployment guide provides a comprehensive approach to deploying the J.K. OVERSEAS PVT.LTD. management system to production. Follow the steps carefully and adapt them to your specific infrastructure requirements.

**Remember**: Always test deployments in a staging environment first! 🚀
