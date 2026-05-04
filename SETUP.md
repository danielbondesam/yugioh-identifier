# Setup Guide - Yu-Gi-Oh Card Identifier

Complete step-by-step setup for local development and testing.

## 📋 Prerequisites

Before you start, ensure you have:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **Tesseract OCR** - See section below

### Installing Tesseract OCR

Tesseract is the core OCR engine. Installation varies by OS.

#### Windows

1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer and note the installation path
3. Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
4. Verify installation:
   ```bash
   "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
   ```

#### macOS (Homebrew)

```bash
brew install tesseract
```

Verify:
```bash
tesseract --version
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

Verify:
```bash
tesseract --version
```

## 🚀 Quick Start (Recommended)

### 1. Clone/Setup Repository

```bash
# Navigate to project directory
cd c:\workflow\projects\yugioh-identifier

# Verify on dev branch
git branch
# Should show: * dev
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# You should see pytest, opencv, tesseract, fastapi, etc. install
```

### 3. Frontend Setup

Open a **NEW terminal window**:

```bash
cd frontend

# Install dependencies
npm install

# Wait for all packages to download (~1-2 min)
```

### 4. Start Backend

In the **first terminal**:

```bash
# Make sure you're in backend folder
cd backend

# Ensure venv is activated (you should see (venv) in your prompt)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
Uvicorn running on http://0.0.0.0:8000
Press CTRL+C to quit
```

### 5. Start Frontend

In the **second terminal**:

```bash
# Make sure you're in frontend folder
cd frontend

npm start
```

Your browser should automatically open at http://localhost:3000

## ✅ Verification

### Check Backend Health

Open a **third terminal** and run:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "cards_loaded": 11000
}
```

### Check Frontend

Visit http://localhost:3000 and verify:
- ✓ Header shows "🎴 Yu-Gi-Oh Identifier"
- ✓ Backend status shows "Backend Online" (green dot)
- ✓ "Open Camera" button is enabled

### API Documentation

Visit http://localhost:8000/docs to see interactive Swagger UI with all endpoints.

## 🔧 Configuration

### Backend Configuration

Create a `.env` file in the `backend` folder:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` to customize:

```python
# Tesseract path (adjust to your installation)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Matching parameters
MIN_CONFIDENCE=0.75           # Minimum confidence to accept match
FUZZY_MATCH_THRESHOLD=80      # Minimum fuzzy match score (0-100)

# Cache settings
CACHE_EXPIRY_HOURS=24         # How often to refresh from API

# ROI dimensions (fixed camera)
FIXED_ROI_WIDTH=400
FIXED_ROI_HEIGHT=600
CARD_NAME_ROI_HEIGHT=80
```

### Frontend Configuration

Create a `.env` file in the `frontend` folder:

```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:

```
REACT_APP_BACKEND_URL=http://localhost:8000
```

If backend is on a different machine:
```
REACT_APP_BACKEND_URL=http://192.168.1.100:8000
```

## 📱 Testing the Application

### Manual Test Flow

1. **Open the app** at http://localhost:3000
2. **Check status** - Green dot should show "Backend Online"
3. **Click "Open Camera"** - Grant camera permissions
4. **Position a card** - Place a Yu-Gi-Oh card in front of camera
5. **Click "📸 Capture"** - Capture the card image
6. **View results** - Card info should display below

### Testing Without Physical Card

You can test with any image containing text:
- Print a card image and photograph it
- Find card images online and take screenshots
- Use the test script (see below)

### Testing via API (curl)

```bash
# Test with an image file
curl -X POST http://localhost:8000/identify_card \
  -F "file=@path/to/card_image.jpg"

# Should return JSON with card details
```

### Running the Test Pipeline

Backend includes development tools for testing:

```bash
cd backend

# Test with generated synthetic images
python test_pipeline.py

# Test with a real image
python test_pipeline.py path/to/card_image.jpg
```

This will output:
- Extracted text from OCR
- Confidence scores
- Matched card name
- Timing breakdown for each stage

## 🐛 Troubleshooting

### Backend won't start

**Error: "ModuleNotFoundError: No module named 'fastapi'"**

```bash
cd backend
python -m pip install -r requirements.txt
```

**Error: "Tesseract is not installed or not in PATH"**

1. Verify Tesseract is installed
2. Update `TESSERACT_PATH` in `backend/app/config.py`
3. Restart backend

**Error: "Port 8000 already in use"**

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use a different port:
python -m uvicorn app.main:app --port 8001
```

### Frontend won't start

**Error: "npm: command not found"**

Install Node.js from https://nodejs.org/

**Error: "Port 3000 already in use"**

```bash
# Kill existing process or use different port
BROWSER=none PORT=3001 npm start
```

**Error: "Module not found"**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Camera not working

1. **Permission denied**
   - Firefox: Settings → Privacy & Security → Permissions → Camera → Allow
   - Chrome: Settings → Privacy & Security → Site Settings → Camera → Allow
   - Safari: System Preferences → Security & Privacy → Camera

2. **No camera detected**
   - Check if camera is enabled on your device
   - Try different browser
   - Restart browser

3. **HTTPS required**
   - Camera API requires HTTPS in production
   - localhost works in development

### Identification not working

1. **Check card is centered** in the ROI (green dashed box)
2. **Improve lighting** - Use bright, even lighting
3. **Check OCR output** - Visit http://localhost:8000/docs
4. **View backend logs** - Look at terminal running backend
5. **Try different angle** - Slight angle changes can help

### Backend returns "Backend Offline"

1. Make sure backend is running: `python -m uvicorn app.main:app...`
2. Check port 8000: `curl http://localhost:8000/health`
3. Check backend logs for errors
4. Verify firewall isn't blocking port 8000

## 📊 First Run Expectations

### First Startup
- Backend: ~10-15 seconds (downloads ~11,000 card database)
- Frontend: ~30 seconds (npm build + start)

### First Identification
- Takes ~1-2 seconds total:
  - ~1s for backend startup (first call)
  - 200-400ms for Tesseract OCR
  - 100ms for fuzzy matching

### Subsequent Identifications
- Takes ~500ms total (cached database)

## 🎯 Next Steps

1. **Read CLAUDE.md** - Understand the architecture
2. **Explore backend API** - Visit http://localhost:8000/docs
3. **Try different cards** - Test with multiple cards
4. **Adjust thresholds** - Fine-tune MIN_CONFIDENCE, FUZZY_MATCH_THRESHOLD
5. **Review logs** - Check backend terminal for debug info

## 📚 Useful Commands

### Backend

```bash
cd backend

# Run with hot reload
python -m uvicorn app.main:app --reload

# Run in production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Test the pipeline
python test_pipeline.py

# Check Tesseract
tesseract --version
```

### Frontend

```bash
cd frontend

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# List cards
curl http://localhost:8000/cards?limit=10

# Refresh cache
curl -X POST http://localhost:8000/refresh_cache

# Identify card (requires image file)
curl -X POST http://localhost:8000/identify_card -F "file=@card.jpg"
```

## 🚀 Deployment

See [CLAUDE.md](CLAUDE.md#-deployment) for deployment instructions.

## 💡 Tips & Best Practices

### For Best OCR Results
- Use good lighting (avoid shadows)
- Position card straight and centered
- Card should fill most of the ROI area
- Avoid glare and reflections

### For Development
- Keep browser DevTools open (F12) for debugging
- Check browser console for frontend errors
- Check backend terminal for server logs
- Use `http://localhost:8000/docs` to test API endpoints directly

### For Performance
- First run downloads database (~10s)
- Subsequent runs use cached database (<1s)
- Tesseract is the bottleneck (~200-300ms per image)
- Fuzzy matching is fast (~100ms for 11k cards)

## 📞 Getting Help

1. **Backend issues**: Check backend terminal for error messages
2. **Frontend issues**: Check browser console (F12)
3. **API issues**: Try http://localhost:8000/docs
4. **Read**: CLAUDE.md for architecture details
5. **Review**: README.md for high-level overview

---

**Status**: Setup complete! Ready to build and test.
