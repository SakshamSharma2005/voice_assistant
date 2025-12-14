# 🧪 API Testing Guide

## Server Status
✅ Server running on: **http://localhost:8000**  
📚 API Documentation: **http://localhost:8000/api/v1/docs**

---

## Method 1: Using Swagger UI (Browser) - **EASIEST**

1. Open **http://localhost:8000/api/v1/docs** in your browser
2. Click on any endpoint to expand it
3. Click **"Try it out"** button
4. Fill in the required parameters
5. Click **"Execute"** to test

### Quick Tests:

#### Test 1: List All Schemes
- Expand `GET /api/v1/schemes/`
- Click "Try it out"
- Click "Execute"
- ✅ Should return all 23 schemes

#### Test 2: Get Specific Scheme
- Expand `GET /api/v1/schemes/{scheme_id}`
- Click "Try it out"
- Enter `PM-KISAN-001` as scheme_id
- Click "Execute"
- ✅ Should return PM Kisan scheme details

#### Test 3: Search Schemes for Farmers
- Expand `POST /api/v1/schemes/search`
- Click "Try it out"
- Paste this JSON:
```json
{
  "occupation": ["farmer"],
  "state": "all"
}
```
- Click "Execute"
- ✅ Should return farming-related schemes with match scores

#### Test 4: Check Eligibility
- Expand `POST /api/v1/eligibility/quick-check`
- Click "Try it out"
- Paste this JSON:
```json
{
  "user_profile": {
    "age": 35,
    "gender": "male",
    "state": "Punjab",
    "occupation": "farmer",
    "annual_income": 80000,
    "has_bank_account": true,
    "has_aadhaar": true,
    "marital_status": "married"
  }
}
```
- Click "Execute"
- ✅ Should return eligible schemes with match percentages

#### Test 5: Start Session
- Expand `POST /api/v1/session/start`
- Click "Try it out"
- Paste this JSON:
```json
{
  "language": "hi",
  "user_context": {
    "age": 30,
    "occupation": "farmer"
  }
}
```
- Click "Execute"
- ✅ Should return session_id and Hindi greeting

#### Test 6: Chat Query (Need session_id from Test 5)
- Expand `POST /api/v1/chat/query`
- Click "Try it out"
- Paste this JSON (replace SESSION_ID with actual ID from Test 5):
```json
{
  "session_id": "sess_xxxxx",
  "query": "I am a farmer looking for financial help",
  "language": "en",
  "user_context": {
    "age": 35,
    "occupation": "farmer",
    "state": "Punjab"
  }
}
```
- Click "Execute"
- ✅ Should return AI-generated response with relevant schemes

#### Test 7: Text-to-Speech
- Expand `POST /api/v1/voice/synthesize`
- Click "Try it out"
- Paste this JSON:
```json
{
  "text": "नमस्ते, मैं आपकी सहायता के लिए यहाँ हूँ",
  "language": "hi"
}
```
- Click "Execute"
- ✅ Should return audio_url (visit URL to download MP3)

---

## Method 2: Using PowerShell/Terminal

### Test 1: Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

### Test 2: List All Schemes
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/schemes/" | ConvertTo-Json -Depth 10
```

### Test 3: Get Specific Scheme
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/schemes/PM-KISAN-001" | ConvertTo-Json -Depth 10
```

### Test 4: Search Schemes
```powershell
$body = @{
    occupation = @("farmer")
    state = "all"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/schemes/search" -Method POST -Body $body -ContentType "application/json"
```

### Test 5: Check Eligibility
```powershell
$body = @{
    user_profile = @{
        age = 35
        gender = "male"
        state = "Punjab"
        occupation = "farmer"
        annual_income = 80000
        has_bank_account = $true
        has_aadhaar = $true
        marital_status = "married"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/eligibility/quick-check" -Method POST -Body $body -ContentType "application/json"
```

---

## Method 3: Using Python Script

Run the test script:
```powershell
python quick_test.py
```

---

## Method 4: Using Postman

1. Import the collection: `postman_collection.json`
2. Set base URL: `http://localhost:8000/api/v1`
3. Run tests from the collection

---

## Expected Results

### All 23 Schemes Loaded:
1. PM-KISAN-001 - Pradhan Mantri Kisan Samman Nidhi
2. AYUSHMAN-BHARAT-002 - Ayushman Bharat
3. PM-AWAS-003 - Pradhan Mantri Awas Yojana
4. MGNREGA-004 - Mahatma Gandhi National Rural Employment Guarantee Act
5. SUKANYA-SAMRIDDHI-005 - Sukanya Samriddhi Yojana
6. PM-SYM-006 - Pradhan Mantri Shram Yogi Maandhan
7. MUDRA-007 - MUDRA Yojana
8. PMUY-008 - Pradhan Mantri Ujjwala Yojana
9. PMJDY-009 - Pradhan Mantri Jan Dhan Yojana
10. PMFBY-010 - Pradhan Mantri Fasal Bima Yojana
11. NSP-011 - National Scholarship Portal
12. PMEGP-012 - Prime Minister's Employment Generation Programme
13. PMKVY-013 - Pradhan Mantri Kaushal Vikas Yojana
14. APY-014 - Atal Pension Yojana
15. BBBP-015 - Beti Bachao Beti Padhao
16. IGNOAPS-016 - Indira Gandhi National Old Age Pension Scheme
17. IGNWPS-017 - Indira Gandhi National Widow Pension Scheme
18. IGNDPS-018 - Indira Gandhi National Disability Pension Scheme
19. PMJJBY-019 - Pradhan Mantri Jeevan Jyoti Bima Yojana
20. PMSBY-020 - Pradhan Mantri Suraksha Bima Yojana
21. STAND-UP-INDIA-021 - Stand-Up India
22. SAMARTH-022 - SAMARTH Scheme
23. POSHAN-ABHIYAAN-023 - POSHAN Abhiyaan

---

## Troubleshooting

### Server Not Running?
```powershell
cd f:\haribhaivoiceasssitant
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Port Already in Use?
```powershell
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Check Logs
Server logs appear in the terminal where uvicorn is running.

---

## Voice Features (Requires Audio Files)

- **Speech-to-Text**: Upload audio file to `/api/v1/voice/transcribe`
- **Text-to-Speech**: Generate audio from text at `/api/v1/voice/synthesize`
- Generated audio files are stored in `storage/audio/` directory
- Audio cache: 24-hour retention

---

## Integration Examples

See `integration_examples.py` for:
- React/React Native integration
- HTML/JavaScript integration  
- Python client example
- WebSocket patterns (future)

---

## Performance Notes

- **Session Timeout**: 30 minutes of inactivity
- **Max Sessions**: 1000 concurrent sessions
- **Cleanup Task**: Runs every 5 minutes
- **Audio Cleanup**: Old files removed after 24 hours
- **AI Response Time**: 2-5 seconds (depends on Gemini API)

---

## 🎉 Happy Testing!

Your Voice-Assisted Government Scheme Navigator API is ready for the hackathon! 🚀
