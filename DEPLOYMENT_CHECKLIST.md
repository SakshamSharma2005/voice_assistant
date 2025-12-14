# ✅ Pre-Deployment Checklist

## 📋 Before Deploying - Verify Everything Works

### Local Testing
- [ ] Server runs without errors: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Health check works: http://localhost:8000/health
- [ ] API docs load: http://localhost:8000/api/v1/docs
- [ ] Chat endpoint works (test in Swagger UI)
- [ ] Voice synthesis works (generates audio files)
- [ ] All 23 schemes load successfully

### Files Check
- [ ] requirements.txt exists and is complete
- [ ] .env.example exists (for reference)
- [ ] Dockerfile exists
- [ ] docker-compose.yml exists
- [ ] render.yaml exists
- [ ] railway.json exists
- [ ] Procfile exists
- [ ] deploy.sh exists
- [ ] README.md exists

### Environment Variables
- [ ] GEMINI_API_KEY is set
- [ ] API key is working (test locally)
- [ ] .env file is NOT in git (add to .gitignore)

### Code Quality
- [ ] No hardcoded secrets in code
- [ ] DEBUG mode is configurable
- [ ] CORS settings are configurable
- [ ] Logging is properly configured

---

## 🚀 Deployment Steps

### Option 1: Render.com (RECOMMENDED - 5 minutes)

**Step 1: Prepare GitHub Repository**
```bash
cd F:/haribhaivoiceasssitant

# Initialize git if not done
git init
git add .
git commit -m "Initial commit - Voice Assisted Scheme Navigator"

# Create repo on GitHub and push
git remote add origin https://github.com/yourusername/your-repo.git
git branch -M main
git push -u origin main
```

**Step 2: Deploy on Render**
1. Go to https://render.com
2. Sign up / Log in
3. Click "New +" → "Web Service"
4. Connect GitHub account
5. Select your repository
6. Render auto-detects Python app
7. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI`
8. Click "Create Web Service"
9. Wait 5-10 minutes for deployment

**Step 3: Test Deployed API**
- Your API will be at: `https://your-service.onrender.com`
- Test: `https://your-service.onrender.com/health`
- Docs: `https://your-service.onrender.com/api/v1/docs`

**✅ Deployment Complete!**

---

### Option 2: Railway.app (Also Easy)

**Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

**Step 2: Deploy**
```bash
cd F:/haribhaivoiceasssitant
railway login
railway init
railway up
```

**Step 3: Add Environment Variables**
```bash
railway variables set GEMINI_API_KEY=AIzaSyCHNOFFWXAjpKvDyjdzwlfxw3gYG_jmuyI
```

**✅ Live at**: `https://your-project.up.railway.app`

---

### Option 3: Ubuntu VPS

**Step 1: Upload Files**
```bash
# From your Windows machine
scp -r F:/haribhaivoiceasssitant user@your-server-ip:/tmp/
```

**Step 2: Run Deploy Script**
```bash
# On your server
ssh user@your-server-ip
cd /tmp/haribhaivoiceasssitant
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

**Step 3: Configure Domain (Optional)**
```bash
# Update Nginx config
sudo nano /etc/nginx/sites-available/scheme-api
# Change: server_name your-domain.com;

# Get SSL
sudo certbot --nginx -d your-domain.com
```

**✅ Live at**: `http://your-server-ip` or `https://your-domain.com`

---

## 🧪 Post-Deployment Testing

### Test These Endpoints:

**1. Health Check**
```bash
curl https://your-deployed-url.com/health
```
Expected: `{"status":"healthy"}`

**2. API Documentation**
```
https://your-deployed-url.com/api/v1/docs
```
Should load Swagger UI

**3. Chat Query**
```bash
curl -X POST https://your-deployed-url.com/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "farmer schemes", "language": "en"}'
```
Should return schemes + audio URL

**4. Voice Synthesis**
```bash
curl -X POST https://your-deployed-url.com/api/v1/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "language": "en"}'
```
Should return audio URL

**5. List Schemes**
```
https://your-deployed-url.com/api/v1/schemes/
```
Should return all 23 schemes

---

## 📊 Monitoring After Deployment

### Check These Regularly:

**Response Times**
- Health check: < 200ms
- Chat query: 3-6 seconds
- Voice synthesis: 2-4 seconds

**Resource Usage**
- Memory: < 1GB for basic load
- CPU: < 50% average
- Disk: Monitor audio folder size

**Error Logs**
- Check for 500 errors
- Monitor Gemini API failures
- Watch for audio generation issues

---

## 🔧 Troubleshooting

### Issue: Server Won't Start
```bash
# Check logs
sudo journalctl -u scheme-api -n 50

# Common fixes:
# 1. Check port 8000 is not in use
# 2. Verify GEMINI_API_KEY is set
# 3. Ensure all dependencies installed
```

### Issue: Audio Not Playing
```bash
# Check ffmpeg is installed
ffmpeg -version

# Check audio directory permissions
ls -la storage/audio/

# Fix permissions
sudo chmod -R 755 storage/
```

### Issue: Gemini API Errors
```bash
# Verify API key
echo $GEMINI_API_KEY

# Test API key manually
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_KEY"
```

### Issue: High Memory Usage
```bash
# Reduce workers
# In start command: --workers 2 (instead of 4)

# Clear old audio files
find storage/audio -type f -mtime +1 -delete
```

---

## 🎉 Deployment Success Indicators

✅ Health endpoint returns 200 OK
✅ Swagger docs load properly
✅ Chat endpoint returns schemes
✅ Audio files are generated
✅ HTTPS is working (if configured)
✅ Response times are acceptable
✅ No errors in logs

---

## 📞 Share Your API

Once deployed, share these URLs:

**API Base URL:**
```
https://your-service.onrender.com/api/v1
```

**API Documentation:**
```
https://your-service.onrender.com/api/v1/docs
```

**Example Request:**
```bash
curl -X POST https://your-service.onrender.com/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "मुझे किसान योजना चाहिए",
    "language": "hi"
  }'
```

---

## 🔐 Security Post-Deployment

**Important:**
1. ✅ Never commit .env file to git
2. ✅ Use HTTPS (free with Render/Railway)
3. ✅ Set proper CORS origins (not *)
4. ✅ Monitor API usage
5. ✅ Keep dependencies updated
6. ✅ Regular backups
7. ✅ Set up rate limiting (if needed)

---

## 📈 Next Steps After Deployment

1. **Monitor Performance**
   - Check response times
   - Monitor error rates
   - Track API usage

2. **Add Features** (Optional)
   - Add database for persistent sessions
   - Implement caching with Redis
   - Add rate limiting
   - Set up logging service (Sentry)

3. **Scale** (If Needed)
   - Increase workers
   - Add load balancer
   - Use CDN for audio files
   - Deploy to multiple regions

---

## 🎯 Estimated Deployment Time

- **Render.com**: 5-10 minutes
- **Railway.app**: 5-10 minutes
- **Ubuntu VPS**: 15-30 minutes (including server setup)
- **Docker**: 10-15 minutes

---

## ✅ You're Ready to Deploy!

Choose your platform and follow the steps above. Your Voice-Assisted Government Scheme Navigator API will be live in minutes! 🚀🇮🇳
