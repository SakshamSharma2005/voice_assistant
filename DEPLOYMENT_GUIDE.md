# 🚀 Deployment Guide - Voice-Assisted Government Scheme Navigator API

## 📋 Prerequisites for Deployment

### 1. Server Requirements
- **OS**: Ubuntu 20.04+ / Debian / CentOS (Linux recommended)
- **RAM**: Minimum 2GB (4GB recommended)
- **CPU**: 2 cores minimum
- **Storage**: 10GB free space
- **Python**: 3.9 or higher
- **Port**: 8000 (or any available port)

### 2. Required Services
- ✅ Python runtime
- ✅ Internet connection (for Gemini AI API)
- ✅ Domain name (optional but recommended)
- ✅ SSL certificate (for HTTPS - recommended)

### 3. API Keys & Credentials
- ✅ Google Gemini API key (already in .env)
- ✅ Domain name (if using custom domain)

---

## 🎯 Deployment Options

### Option 1: Deploy on Cloud (Recommended)
- **Render** (Free tier available) ✨ EASIEST
- **Railway** (Free tier available)
- **AWS EC2** (Pay as you go)
- **Google Cloud Run** (Pay as you go)
- **Azure App Service** (Pay as you go)
- **DigitalOcean** (Starting $5/month)

### Option 2: Deploy on VPS
- **Linode** ($5/month)
- **Vultr** ($5/month)
- **Hetzner** (€4/month)

### Option 3: Deploy Locally/On-Premise
- Your own server
- Local network deployment

---

## 🌟 EASIEST: Deploy to Render (Free Tier)

### Step-by-Step for Render.com:

**1. Prepare Project for Deployment**

Create `render.yaml`:
```yaml
services:
  - type: web
    name: government-scheme-navigator
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        value: AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: "*"
```

**2. Sign up at Render.com**
- Go to https://render.com
- Sign up with GitHub

**3. Create New Web Service**
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Or use "Deploy from GitHub URL"

**4. Configure Service**
- Name: `government-scheme-navigator`
- Environment: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Instance Type: Free

**5. Add Environment Variables**
- GEMINI_API_KEY = `AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI`
- ENVIRONMENT = `production`

**6. Deploy!**
- Click "Create Web Service"
- Wait 5-10 minutes
- Your API will be live at: `https://your-service.onrender.com`

---

## 🐳 RECOMMENDED: Deploy with Docker

### Step 1: Create Production Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/audio storage/temp logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Build and Run

```bash
# Build image
docker build -t govt-scheme-api .

# Run container
docker run -d \\
  -p 8000:8000 \\
  -e GEMINI_API_KEY=AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI \\
  -e ENVIRONMENT=production \\
  --name scheme-api \\
  govt-scheme-api
```

### Step 3: Deploy to Cloud (Docker)

**Push to Docker Hub:**
```bash
docker tag govt-scheme-api yourusername/govt-scheme-api
docker push yourusername/govt-scheme-api
```

**Deploy on any cloud that supports Docker!**

---

## 🖥️ Deploy on Ubuntu VPS

### Step-by-Step:

**1. Connect to Server**
```bash
ssh user@your-server-ip
```

**2. Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install ffmpeg
sudo apt install ffmpeg -y

# Install nginx (for reverse proxy)
sudo apt install nginx -y
```

**3. Upload Your Project**
```bash
# Option A: Using git
cd /var/www
sudo git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Option B: Using SCP from local machine
scp -r F:/haribhaivoiceasssitant user@server-ip:/var/www/
```

**4. Setup Python Environment**
```bash
cd /var/www/haribhaivoiceasssitant

# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**5. Configure Environment**
```bash
# Create production .env
nano .env
```

Add:
```env
GEMINI_API_KEY=AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI
ENVIRONMENT=production
CORS_ORIGINS=*
HOST=0.0.0.0
PORT=8000
```

**6. Setup Systemd Service**
```bash
sudo nano /etc/systemd/system/scheme-api.service
```

Add:
```ini
[Unit]
Description=Government Scheme Navigator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/haribhaivoiceasssitant
Environment="PATH=/var/www/haribhaivoiceasssitant/venv/bin"
ExecStart=/var/www/haribhaivoiceasssitant/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**7. Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable scheme-api
sudo systemctl start scheme-api
sudo systemctl status scheme-api
```

**8. Configure Nginx (Reverse Proxy)**
```bash
sudo nano /etc/nginx/sites-available/scheme-api
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/v1/audio/ {
        proxy_pass http://localhost:8000;
        proxy_buffering off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/scheme-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**9. Setup SSL (HTTPS)**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

**10. Open Firewall**
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

---

## ☁️ Deploy on Railway.app

### Steps:

**1. Install Railway CLI**
```bash
npm i -g @railway/cli
```

**2. Login**
```bash
railway login
```

**3. Initialize Project**
```bash
cd F:/haribhaivoiceasssitant
railway init
```

**4. Add Environment Variables**
```bash
railway variables set GEMINI_API_KEY=AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI
railway variables set ENVIRONMENT=production
```

**5. Deploy**
```bash
railway up
```

Your API will be live at: `https://your-project.up.railway.app`

---

## 🔧 Production Configuration Changes

### 1. Update .env for Production

```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# API Keys
GEMINI_API_KEY=AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI

# CORS (adjust for your frontend domain)
CORS_ORIGINS=https://yourfrontend.com,https://www.yourfrontend.com

# Limits
MAX_SESSIONS=10000
SESSION_TIMEOUT_MINUTES=30
MAX_AUDIO_FILE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO
```

### 2. Update requirements.txt

Ensure you have:
```txt
fastapi==0.124.4
uvicorn[standard]==0.38.0
pydantic==2.10.4
pydantic-settings==2.7.1
google-generativeai==0.8.3
gtts==2.5.4
pydub==0.25.1
SpeechRecognition==3.14.4
langdetect==1.0.9
tenacity==9.0.0
python-multipart==0.0.20
aiofiles==24.1.0
gunicorn==23.0.0
```

### 3. Add Gunicorn for Production

Install:
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 📊 Monitoring & Maintenance

### 1. Check Logs
```bash
# Systemd service logs
sudo journalctl -u scheme-api -f

# Or application logs
tail -f logs/app.log
```

### 2. Monitor Performance
```bash
# Check CPU/Memory
htop

# Check disk space
df -h

# Check API health
curl http://localhost:8000/health
```

### 3. Auto-cleanup Audio Files

Add to crontab:
```bash
crontab -e
```

Add line:
```bash
0 2 * * * find /var/www/haribhaivoiceasssitant/storage/audio -type f -mtime +1 -delete
```

---

## 🔒 Security Checklist

- [ ] Change default API keys
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly (don't use * in production)
- [ ] Set up firewall rules
- [ ] Disable debug mode
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Monitor API usage
- [ ] Set rate limiting
- [ ] Backup data regularly

---

## 🧪 Test Deployed API

Once deployed, test with:

```bash
# Health check
curl https://your-domain.com/health

# API docs
https://your-domain.com/api/v1/docs

# Test query
curl -X POST https://your-domain.com/api/v1/chat/query \\
  -H "Content-Type: application/json" \\
  -d '{"query": "farmer schemes", "language": "en"}'
```

---

## 📈 Scaling Options

### Horizontal Scaling
- Add more server instances
- Use load balancer (Nginx, AWS ALB)
- Deploy across multiple regions

### Vertical Scaling
- Increase server RAM/CPU
- Optimize workers count
- Use caching (Redis)

### Database
- Add MongoDB for persistent sessions
- Use Redis for caching

---

## 💰 Cost Estimates

### Free Tier Options
- **Render Free**: Good for demo/testing
- **Railway Free**: $5 credit/month
- **Fly.io Free**: Limited resources

### Paid Options
- **DigitalOcean**: $5-10/month
- **AWS EC2 t2.micro**: ~$8/month
- **Render Starter**: $7/month
- **Railway**: Pay as you go (~$5-10/month)

---

## 📞 Post-Deployment

### Update DNS
Point your domain to server IP:
```
A Record: @ → your-server-ip
A Record: www → your-server-ip
```

### Share API
- Documentation: https://your-domain.com/api/v1/docs
- Base URL: https://your-domain.com/api/v1
- Health: https://your-domain.com/health

---

## 🎉 Deployment Complete!

Your Voice-Assisted Government Scheme Navigator API is now live! 🚀

**Next Steps:**
1. Monitor logs for any issues
2. Test all endpoints
3. Share API documentation
4. Set up monitoring (optional: Sentry, DataDog)
5. Configure auto-scaling (if needed)
