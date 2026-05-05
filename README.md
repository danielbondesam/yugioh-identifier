# Yu-Gi-Oh Card Identifier

A production-ready MVP for identifying Yu-Gi-Oh trading cards using smartphone camera capture with fixed camera placement, OCR, and fuzzy matching.

## 🎯 Features

- **📷 Real-time Camera Capture** - Browser-based camera access using MediaDevices API
- **🎴 Card Identification** - Extract card names and codes via Tesseract OCR
- **📊 Dual OCR Pipeline** - Separate extraction for card name (top region) and card code (bottom region)
- **🔍 Fuzzy Matching** - Intelligent card matching against YGOPRODeck database
- **📈 Advanced Confidence Scoring** - Combined score from 4 independent signals:
  - Name OCR extraction confidence
  - Card code OCR confidence
  - Fuzzy matching confidence
  - Image quality metrics
- **🎚️ Image Quality Analysis** - Automatic assessment of brightness, contrast, sharpness, motion blur, and noise
- **💡 Smart Suggestions** - Actionable feedback based on image quality and extraction confidence
- **🚨 Review Flags** - Identifies low-confidence matches requiring manual review
- **💾 Local Caching** - Automatic database caching with expiry management
- **📱 Mobile-First UI** - Tailwind CSS responsive design optimized for smartphone cameras
- **🎯 Fixed ROI** - Optimized for fixed camera placement (eliminates heavy detection models)

## 🏗️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling and responsive design
- **MediaDevices API** - Camera access
- **Canvas API** - Image capture and processing

### Backend
- **FastAPI** - Python web framework
- **OpenCV** - Image preprocessing
- **Tesseract OCR** - Text extraction from images
- **FuzzyWuzzy** - Fuzzy string matching
- **YGOPRODeck API** - Card database source

### Architecture
- **Two separate services** - Frontend (React) and Backend (FastAPI)
- **RESTful API** - JSON request/response
- **Local JSON caching** - Efficient card database storage

## 📋 Installation (Detailed – Windows)

### 1) Install Python

**Download:** https://www.python.org/downloads/

During installation:
- Check "Add Python to PATH"
- Click "Install Now"

**Verify installation:**

```bash
python --version
pip --version
```

If pip is not recognized:

```bash
python -m pip --version
```

### 2) Install Node.js

**Download:** https://nodejs.org/
Install the **LTS version**

**Verify:**

```bash
node -v
npm -v
```

### 3) Install Tesseract OCR

**Download (Windows build):** https://github.com/tesseract-ocr/tesseract

**Default install path:**

```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If needed, add to PATH:
- Control Panel → System → Environment Variables → PATH
- Add: `C:\Program Files\Tesseract-OCR\`

**Verify:**

```bash
tesseract --version
```

### ⚙️ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

If pip is not recognized:

```bash
python -m pip install -r requirements.txt
```

**Run backend:**

```bash
uvicorn app.main:app --reload
```

### 💻 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### ▶️ How to Run (Quick)

1. Start backend
2. Start frontend
3. Open browser (mobile or desktop)
4. Allow camera access
5. Position the card inside the ROI
6. Capture and identify

## 🚀 Running the Project

### Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

API documentation (Swagger UI): **http://localhost:8000/docs**

### Start Frontend (new terminal)

```bash
cd frontend
npm start
```

Frontend will open at: **http://localhost:3000**

## 📖 How to Use (End User)

1. **Open the app** - Navigate to http://localhost:3000
2. **Check backend status** - Look for green "Backend Online" indicator in top-right
3. **Click "Open Camera"** - Grant camera permissions when prompted
4. **Position card** - Place your Yu-Gi-Oh card in the center of the screen
   - Card should be well-lit and clearly visible
   - The green dashed box shows the optimal placement area
5. **Capture image** - Click "📸 Capture" button
6. **View results** - Card name, stats, image, and description appear below
7. **Try again** - Click "Scan Another Card" to identify more cards

## 🔧 API Endpoints

### `POST /identify_card`
Identify a card from an uploaded image.

**Request:**
```
Content-Type: multipart/form-data
Body: image file
```

**Response (Success):**
```json
{
  "success": true,
  "name": "Blue-Eyes White Dragon",
  "type": "Synchro/Effect Monster",
  "confidence": 0.95,
  "ocr_confidence": 0.92,
  "match_score": 98,
  "atk": 3000,
  "def": 2500,
  "level": 8,
  "attribute": "LIGHT",
  "race": "Dragon",
  "description": "...",
  "image_url": "..."
}
```

### `GET /health`
Check backend health status.

```json
{
  "status": "healthy",
  "cards_loaded": 11000
}
```

### `GET /cards?limit=100&offset=0`
Get paginated list of available cards.

### `POST /refresh_cache`
Force refresh card database from YGOPRODeck API.

## 🗂️ Project Structure

```
.
├── frontend/                    # React application
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraCapture.js    # Camera and ROI overlay
│   │   │   ├── ResultDisplay.js    # Card results view
│   │   │   └── Header.js           # App header with status
│   │   ├── App.js                  # Main component
│   │   ├── index.js                # React entry point
│   │   └── index.css               # Tailwind styles
│   ├── package.json
│   ├── tailwind.config.js
│   └── README.md
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py                 # FastAPI app and routes
│   │   ├── config.py               # Configuration constants
│   │   ├── image_processor.py      # Image preprocessing pipeline
│   │   ├── ocr_engine.py           # Tesseract OCR wrapper
│   │   ├── card_code_extractor.py  # Card code extraction and validation
│   │   ├── image_quality.py        # Image quality analysis
│   │   ├── card_matcher.py         # Fuzzy matching logic
│   │   ├── card_cache.py           # YGOPRODeck API and caching
│   │   └── __init__.py
│   ├── requirements.txt
│   └── README.md
│
├── README.md                    # This file
└── CLAUDE.md                    # Architecture documentation
```

## 🔄 Data Pipeline

### Enhanced 7-Step OCR Pipeline (v2)

The improved pipeline combines name extraction, card code recognition, image quality analysis, and fuzzy matching for comprehensive card identification:

```
1. IMAGE CAPTURE → 2. CROP ROI → 3. QUALITY CHECK → 4. NAME EXTRACTION → 
5. CODE EXTRACTION → 6. FUZZY MATCH → 7. CONFIDENCE SCORING → RESULT
```

#### Step-by-Step Process

**Step 1: Fixed ROI Extraction (400×600px)**
- Crops center region of captured image
- Fixed dimensions work with fixed camera placement
- O(1) operation with no object detection

**Step 2: Image Quality Assessment**
- Calculates brightness, contrast, and sharpness metrics
- Detects motion blur using edge analysis
- Estimates noise level with median filtering
- **Composite quality score** from weighted metrics:
  - 30% sharpness (most important)
  - 25% contrast
  - 20% motion blur
  - 15% brightness
  - 10% noise
- Returns `is_acceptable` flag (threshold: 0.60)

**Step 3: Card Name Extraction (top 80px)**
- Preprocesses region with adaptive threshold
- Applies morphological operations
- Upscales 2x for better OCR accuracy
- Tesseract extracts text with confidence scoring
- Returns: (name_text, ocr_confidence)

**Step 4: Card Code Extraction (bottom region)**
- Dedicated ROI for code region (bottom ~60px)
- **More aggressive preprocessing** for small text:
  - 3x upscaling (vs 2x for name)
  - Higher adaptive threshold block size
  - Morphological close for connected characters
- Validates against Yu-Gi-Oh code patterns:
  - Passcode format: `25345090-1` (8 digits-digit)
  - Release format: `SDK-001` (code-numbers)
  - Handles whitespace and normalization
- Returns: (validated_code, ocr_confidence, is_valid)

**Step 5: Fuzzy Matching**
- Compares extracted name against 11,000+ card database
- Uses token sort ratio to handle word reordering
- Returns best match or top-N candidates
- Provides fuzzy_confidence score

**Step 6: Combined Confidence Scoring**
- Integrates 4 independent signals:
  ```
  combined_confidence = 
    (30% × name_ocr_confidence) +
    (40% × fuzzy_match_confidence) +
    (15% × code_ocr_confidence) +
    (15% × image_quality_score)
  ```
- **Why these weights?**
  - Fuzzy matching is most reliable (40%)
  - Name OCR is primary signal (30%)
  - Image quality indicates reliability (15%)
  - Card code validates identity (15%)

**Step 7: Quality & Suggestions**
- Sets `needs_review` flag if:
  - `combined_confidence < 0.80`, OR
  - Card code validation failed, OR
  - Image quality unacceptable
- Generates actionable suggestions based on failures:
  - "Image is blurry" (sharpness < 0.5)
  - "Image too dark/bright" (brightness issues)
  - "Too much noise" (noise > 0.5)
  - "Card code not visible"
  - "Try repositioning"

#### Response Format

```json
{
  "success": true,
  "name": "Blue-Eyes White Dragon",
  "code": "25345090",
  "card_id": 25345090,
  "confidence": 0.94,
  "source": "combined_pipeline",
  "needs_review": false,
  "suggestions": [],
  "metrics": {
    "name_ocr": 0.92,
    "code_ocr": 0.88,
    "code_valid": true,
    "fuzzy_match": 0.96,
    "image_quality": 0.91,
    "quality_breakdown": {
      "brightness": 0.85,
      "contrast": 0.89,
      "sharpness": 0.95,
      "motion_blur": 0.92,
      "noise": 0.80
    }
  },
  "extracted_text": {
    "name": "BLUE EYES WHITE DRAGON",
    "code": "25345090"
  },
  "type": "Synchro/Effect Monster",
  "atk": 3000,
  "def": 2500,
  "level": 8,
  "attribute": "LIGHT",
  "race": "Dragon",
  "description": "...",
  "image_url": "..."
}
```

### Configuration

Key pipeline parameters in `backend/app/config.py`:

```python
# ROI Settings
FIXED_ROI_WIDTH = 400
FIXED_ROI_HEIGHT = 600
CARD_NAME_ROI_HEIGHT = 80
CARD_CODE_ROI_TOP = 500
CARD_CODE_ROI_HEIGHT = 60

# Thresholds
IMAGE_QUALITY_THRESHOLD = 0.60
MIN_CONFIDENCE = 0.75

# Confidence Weighting
NAME_OCR_WEIGHT = 0.30
CODE_OCR_WEIGHT = 0.15
FUZZY_MATCH_WEIGHT = 0.40
IMAGE_QUALITY_WEIGHT = 0.15
```

## 🔄 Legacy Data Pipeline (v1)

1. **Image Capture** - User captures image from camera
2. **ROI Extraction** - Fixed region (400x600px) cropped from center
3. **Name Region** - Top 80px extracted for OCR
4. **Preprocessing** - Grayscale → threshold → contrast → sharpen → upscale
5. **OCR** - Tesseract extracts text with confidence score
6. **Matching** - FuzzyWuzzy matches against YGOPRODeck database
7. **Scoring** - Combined confidence = 40% OCR + 60% fuzzy match
8. **Result** - Return matched card or top candidates

## 🎯 Optimization Strategy

### Fixed Camera Approach
- **No YOLO/heavy detection** - Fixed placement eliminates need for object detection
- **Deterministic ROI** - Always crops from center at fixed dimensions
- **Fast processing** - <500ms end-to-end on modest hardware
- **Offline capable** - All processing can run locally

### OCR Tuning
- **Adaptive threshold** - Handles variable lighting conditions
- **Upscaling** - 2x zoom improves text recognition
- **Denoising** - Median blur reduces noise artifacts
- **Contrast enhancement** - Makes text sharper and more distinct

### Matching Strategy
- **Token sort ratio** - Handles word reordering in card names
- **Confidence combination** - Weights OCR + fuzzy together
- **Fallback candidates** - Shows top N matches if no exact hit
- **Threshold filtering** - Only returns confident matches

## 🚀 Performance Targets

- **<500ms** total identification time (web MVP)
- **>90%** accuracy on well-lit, centered cards
- **11,000+** card database from YGOPRODeck

## 📱 Future Roadmap

### Stage 2: Mobile App (On-Device)
- Export OCR model to TensorFlow Lite / ONNX
- Bundle card database as SQLite in app
- 100% offline operation
- <300ms real-time identification
- No backend dependency

### Stage 3: Advanced Features
- Batch scanning (multiple cards)
- Historical scan log
- Deck building integration
- Multi-language support

## 🛠️ Development

### Backend Development

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm start
```

### Testing Backend API

```bash
# Using curl
curl -X POST http://localhost:8000/identify_card \
  -F "file=@path/to/card_image.jpg"

# Or visit Swagger UI
http://localhost:8000/docs
```

## 📝 Configuration

### Backend Configuration

Edit [backend/app/config.py](backend/app/config.py):

**Image Processing:**
- `FIXED_ROI_WIDTH` / `FIXED_ROI_HEIGHT` - Card region dimensions (400x600)
- `CARD_NAME_ROI_HEIGHT` - Top region height for name extraction (80px)
- `CARD_CODE_ROI_TOP` / `CARD_CODE_ROI_HEIGHT` - Card code location (bottom ~60px)

**Quality & Matching Thresholds:**
- `IMAGE_QUALITY_THRESHOLD` - Minimum acceptable image quality score (default: 0.50)
  - 0-1 scale; lower values are more lenient with poor lighting
  - Set to 0.50 for low-light environments
- `FUZZY_MATCH_THRESHOLD` - Minimum fuzzy matching score (default: 70)
  - 0-100 scale; lower values accept more loosely matching card names
  - Reduced to 70 from 80 for improved low-light tolerance
- `MIN_CONFIDENCE` - Minimum combined confidence to return result (default: 0.65)
  - 0-1 scale; lower values allow accepting lower-confidence identifications
  - Reduced to 0.65 from 0.75 for difficult lighting conditions

**Caching:**
- `CACHE_EXPIRY_HOURS` - How long to keep cached cards (default: 24)

### Tesseract Path

If Tesseract is installed in a non-standard location, set the path in [backend/app/config.py](backend/app/config.py):

```python
TESSERACT_PATH = r"C:\path\to\tesseract.exe"  # Windows
TESSERACT_PATH = "/usr/bin/tesseract"  # Linux
```

## 🔧 Tuning for Lighting Conditions

If experiencing low identification rates in your lighting environment:

**Reduce thresholds** in [backend/app/config.py](backend/app/config.py):
- Lower `IMAGE_QUALITY_THRESHOLD` (e.g., 0.40 for very poor lighting)
- Lower `FUZZY_MATCH_THRESHOLD` (e.g., 60 for lenient matching)
- Lower `MIN_CONFIDENCE` (e.g., 0.55 for accepting lower-confidence results)

**Preprocessing improvements** (already applied):
- CLAHE contrast enhancement set to `clipLimit=3.0` (aggressive)
- Preprocessing pipeline: upscale BEFORE contrast enhancement
- Brightness scoring range widened to accommodate low-light

**Recommendations for best results:**
- Use fixed camera mount for consistent framing
- Provide direct even lighting on card (avoid shadows)
- Test with printed 3D camera mount for 100% steady positioning
- Gradually adjust thresholds if specific lighting is permanent

## ⚠️ Known Limitations

- Requires fixed camera placement for optimal performance
- Lighting quality significantly affects OCR accuracy (optimal: 40-225 brightness range)
- Large file sizes on first API call (downloads full card database)
- Card image URLs must be accessible (YGOPRODeck external images)
- Very low resolution images (<250px) may require additional preprocessing tuning

## 📄 License

[Add your license here]

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for detailed architecture documentation.

## 📞 Support

For issues or questions:
1. Check backend is running on port 8000 (`/health` endpoint)
2. Verify Tesseract is installed and accessible
3. Review backend logs for OCR errors
4. Check browser console for frontend errors
