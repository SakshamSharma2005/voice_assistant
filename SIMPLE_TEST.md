# 🧪 Simple Testing Guide

## ✅ Is Server Running?

Open browser: http://localhost:8000/health

Should show: `{"status": "healthy"}`

---

## 🎯 3 Simple Ways to Test

### 1️⃣ Browser (Easiest - No Coding!)

**Step 1:** Open http://localhost:8000/api/v1/docs

**Step 2:** Find **"Chat & Query"** section

**Step 3:** Click **POST /api/v1/chat/query**

**Step 4:** Click **"Try it out"**

**Step 5:** Paste this:
```json
{
  "query": "I need farmer schemes",
  "language": "en"
}
```

**Step 6:** Click **"Execute"**

**Step 7:** Look for `response_audio_url` in response

**Step 8:** Click the audio URL to hear the voice!

---

### 2️⃣ PowerShell (Quick One-Liner)

Copy and paste this command:

```powershell
$body = @{ query = "I need farmer schemes"; language = "en" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/chat/query" -Method POST -Body $body -ContentType "application/json"
```

You'll see:
- AI response text
- List of schemes
- Audio URL

---

### 3️⃣ Python Script

Run:
```bash
python test_voice_flow.py
```

Or:
```bash
python quick_test.py
```

---

## 🎤 Test Voice Features

### Generate Voice (Text → Audio)

**Browser:**
1. Go to http://localhost:8000/api/v1/docs
2. Find **POST /api/v1/voice/synthesize**
3. Click "Try it out"
4. Paste:
```json
{
  "text": "Hello, welcome to Government Schemes",
  "language": "en"
}
```
5. Click "Execute"
6. Copy `audio_url` and open in browser

**PowerShell:**
```powershell
$body = @{ text = "Hello"; language = "en" } | ConvertTo-Json
$r = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/voice/synthesize" -Method POST -Body $body -ContentType "application/json"
Start-Process "http://localhost:8000$($r.audio_url)"
```

---

## 📋 Test Scheme Endpoints

### List All Schemes
```
http://localhost:8000/api/v1/schemes/
```

### Get Specific Scheme
```
http://localhost:8000/api/v1/schemes/PM-KISAN-001
```

### Search Schemes
**Browser:** Use Swagger UI at POST /api/v1/schemes/search

**PowerShell:**
```powershell
$body = @{ occupation = @("farmer") } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/schemes/search" -Method POST -Body $body -ContentType "application/json"
```

---

## 🔍 What to Check

✅ **Response contains:**
- `success: true`
- `response_text` with AI answer
- `response_audio_url` with audio file
- `schemes` array with matching schemes

✅ **Audio URL should:**
- Start with `/api/v1/audio/`
- End with `.mp3`
- Be playable in browser when opened

✅ **Schemes should:**
- Have Hindi and English names
- Show helpline numbers
- Include website links

---

## 🎧 Listen to Audio

Copy any audio URL like:
```
/api/v1/audio/tts_xxxxx.mp3
```

Open in browser:
```
http://localhost:8000/api/v1/audio/tts_xxxxx.mp3
```

Or use PowerShell:
```powershell
Start-Process "http://localhost:8000/api/v1/audio/tts_xxxxx.mp3"
```

---

## 🌐 Test Different Languages

### Hindi
```json
{
  "query": "मुझे किसान योजना चाहिए",
  "language": "hi"
}
```

### English
```json
{
  "query": "I need farmer schemes",
  "language": "en"
}
```

### Tamil
```json
{
  "query": "எனக்கு விவசாய திட்டங்கள் வேண்டும்",
  "language": "ta"
}
```

---

## ❌ Troubleshooting

**Server not responding?**
```powershell
# Check if running
Get-Process python

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Port 8000 busy?**
```powershell
# Kill existing process
Stop-Process -Name python -Force
```

**Audio not playing?**
- Check if file exists in `storage/audio/`
- Make sure URL includes full path
- Try opening in different browser

---

## 📊 Expected Response Example

```json
{
  "success": true,
  "data": {
    "response_text": "I found 5 schemes for farmers...",
    "response_audio_url": "/api/v1/audio/tts_xxxxx.mp3",
    "language": "en",
    "schemes": [
      {
        "scheme_id": "PM-KISAN-001",
        "name": "PM Kisan Samman Nidhi",
        "helpline": "155261"
      }
    ]
  },
  "metadata": {
    "processing_time_ms": 4500
  }
}
```

---

## ✅ Quick Checklist

- [ ] Server running on http://localhost:8000
- [ ] Health check returns "healthy"
- [ ] Swagger UI loads at /api/v1/docs
- [ ] Chat query returns response
- [ ] Audio URL is generated
- [ ] Audio file plays in browser
- [ ] Schemes are returned
- [ ] Multiple languages work

---

## 🎉 Success Indicators

✅ Response time: 3-6 seconds
✅ Audio file size: 50-200 KB
✅ Schemes found: 1-10 (depending on query)
✅ Audio plays in browser
✅ Hindi/English both work

---

## 🚀 Ready for Demo!

Your API is working if:
1. ✅ You can query in Hindi/English
2. ✅ You get AI response with schemes
3. ✅ Audio URL is returned
4. ✅ Audio plays when you click it

**All 23 government schemes + Voice + AI = Complete! 🎉**
