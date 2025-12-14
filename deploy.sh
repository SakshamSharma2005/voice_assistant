# 🚀 Quick Deployment Script for Ubuntu Server

# This script automates the deployment process

#!/bin/bash

echo "🚀 Starting deployment..."

# 1. Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.11
echo "🐍 Installing Python..."
sudo apt install python3.11 python3.11-venv python3-pip ffmpeg nginx -y

# 3. Create app directory
echo "📁 Setting up application..."
sudo mkdir -p /var/www/scheme-api
cd /var/www/scheme-api

# 4. Clone or copy your code here
# git clone https://github.com/yourusername/your-repo.git .
# Or manually upload files

# 5. Create virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# 6. Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Create .env file
echo "⚙️ Creating environment file..."
cat > .env << EOL
GEMINI_API_KEY=AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=*
LOG_LEVEL=INFO
EOL

# 8. Create directories
mkdir -p storage/audio storage/temp logs

# 9. Create systemd service
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/scheme-api.service > /dev/null << EOL
[Unit]
Description=Government Scheme Navigator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/scheme-api
Environment="PATH=/var/www/scheme-api/venv/bin"
ExecStart=/var/www/scheme-api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# 10. Start service
echo "▶️ Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable scheme-api
sudo systemctl start scheme-api

# 11. Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/scheme-api > /dev/null << 'EOL'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    location /api/v1/audio/ {
        proxy_pass http://localhost:8000;
        proxy_buffering off;
    }
}
EOL

sudo ln -s /etc/nginx/sites-available/scheme-api /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 12. Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
echo "y" | sudo ufw enable

# 13. Setup auto-cleanup cron job
echo "🗑️ Setting up audio cleanup..."
(crontab -l 2>/dev/null; echo "0 2 * * * find /var/www/scheme-api/storage/audio -type f -mtime +1 -delete") | crontab -

# 14. Check status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service status:"
sudo systemctl status scheme-api --no-pager

echo ""
echo "🧪 Testing API..."
sleep 5
curl http://localhost:8000/health

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment successful!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Your API is running at:"
echo "   Local: http://localhost:8000"
echo "   Public: http://$(curl -s ifconfig.me):8000"
echo ""
echo "📚 API Documentation:"
echo "   http://$(curl -s ifconfig.me):8000/api/v1/docs"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status scheme-api   # Check status"
echo "   sudo systemctl restart scheme-api  # Restart service"
echo "   sudo journalctl -u scheme-api -f   # View logs"
echo "   sudo nginx -t                      # Test nginx config"
echo ""
echo "🔐 Next steps:"
echo "   1. Configure your domain DNS"
echo "   2. Run: sudo certbot --nginx -d yourdomain.com"
echo "   3. Update CORS_ORIGINS in .env"
echo ""
