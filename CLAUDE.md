# Yu-Gi-Oh Identifier - Architecture & Design Document

Internal technical documentation for architects and engineers.

## 🎯 System Overview

This is a **two-stage system design**:

- **Stage 1 (Current)**: Web MVP with fixed camera, backend processing
- **Stage 2 (Future)**: Mobile app with on-device execution

The architecture is intentionally designed to facilitate easy migration from web to mobile.

## 🏗️ Stage 1: Web MVP Architecture (Enhanced v2)

```
┌──────────────────────────────────────────────────────────┐
│                  Browser (React)                          │
│  ┌──────────────────────┐     ┌─────────────────────┐   │
│  │  CameraCapture       │     │ ResultDisplay       │   │
│  │  Component           │────→│ Component           │   │
│  │                      │     │                     │   │
│  │ - getUserMedia       │     │ - Card info         │   │
│  │ - Canvas capture     │     │ - Metrics display   │   │
│  │ - Blob encode        │     │ - Quality feedback  │   │
│  └──────────┬───────────┘     │ - Suggestions       │   │
│             │                  └─────────────────────┘   │
│      FormData (blob)                                      │
└─────────────┼──────────────────────────────────────────────┘
              │ HTTP POST
              ▼
┌──────────────────────────────────────────────────────────┐
│         FastAPI Backend (Python) - Enhanced Pipeline    │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  POST /identify_card (7-Step Pipeline)             │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────┐    │ │
│  │  │ 1. IMAGE RECEPTION & ROI CROP (400x600) │    │ │
│  │  │    └─ ImageProcessor.crop_fixed_roi()   │    │ │
│  │  └──────────────────────────────────────────┘    │ │
│  │                    ▼                              │ │
│  │  ┌──────────────────────────────────────────┐    │ │
│  │  │ 2. QUALITY ASSESSMENT                    │    │ │
│  │  │    └─ ImageQualityAnalyzer.assess()     │    │ │
│  │  │       • Brightness, contrast, sharpness │    │ │
│  │  │       • Motion blur, noise detection    │    │ │
│  │  │       • Composite score (0-1)           │    │ │
│  │  └──────────────────────────────────────────┘    │ │
│  │                    ▼                              │ │
│  │  ┌──────────────────────────────────────────┐    │ │
│  │  │ 3. NAME EXTRACTION (Top 80px)            │    │ │
│  │  │    ├─ Extract region                     │    │ │
│  │  │    ├─ Preprocess (threshold, sharpen)    │    │ │
│  │  │    └─ OCREngine.extract_card_name()      │    │ │
│  │  │       → (name_text, ocr_confidence)      │    │ │
│  │  └──────────────────────────────────────────┘    │ │
│  │                    ▼                              │ │
│  │  ┌──────────────────────────────────────────┐    │ │
│  │  │ 4. CODE EXTRACTION (Bottom ~60px)        │    │ │
│  │  │    ├─ Extract region (ROI_TOP=500)       │    │ │
│  │  │    ├─ Aggressive preprocessing (3x zoom) │    │ │
│  │  │    ├─ CardCodeExtractor.extract_and_...  │    │ │
│  │  │    └─ Regex validation vs patterns       │    │ │
│  │  │       → (code, is_valid, confidence)    │    │ │
│  │  │       • Passcode: \d{8}-\d+             │    │ │
│  │  │       • Release: [A-Z]{2,4}-\d{3,4}    │    │ │
│  │  └──────────────────────────────────────────┘    │ │
│  │                    ▼                              │ │
│  │  ┌──────────────────────────────────────────┐    │ │
│  │  │ 5. FUZZY MATCHING                        │    │ │
│  │  │    └─ CardMatcher.find_best_match()      │    │ │
│  │  │       • Token sort ratio matching        │    │ │
│  │  │       • 11,000+ cards database           │    │ │
│  │  │       → (card_dict, confidence)          │    │ │
│  │  └──────────────────────────────────────────┘    │ │
│  │                    ▼                              │ │
│  │  ┌──────────────────────────────────────────┐    │ │
│  │  │ 6. CONFIDENCE AGGREGATION                │    │ │
│  │  │    combined_score =                      │    │ │
│  │  │      0.30 × name_ocr_conf +             │    │ │
│  │  │      0.40 × fuzzy_match_conf +          │    │ │
│  │  │      0.15 × code_ocr_conf +             │    │ │
│  │  │      0.15 × image_quality_score         │    │ │
│  │  └──────────────────────────────────────────┘    │ │
│  │                    ▼                              │ │
│  │  ┌──────────────────────────────────────────┐    │ │
│  │  │ 7. RESULT GENERATION & FEEDBACK          │    │ │
│  │  │    ├─ needs_review flag (< 0.80 or QA) │    │ │
│  │  │    ├─ Actionable suggestions             │    │ │
│  │  │    ├─ Full metrics breakdown             │    │ │
│  │  │    └─ source: "combined_pipeline"        │    │ │
│  │  └──────────────────────────────────────────┘    │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  External Dependencies                             │ │
│  │  • CardCache → YGOPRODeck API (cached 24h)        │ │
│  │  • Tesseract OCR (system binary)                  │ │
│  │  • FuzzyWuzzy (token sort matching)               │ │
│  │  • OpenCV (image processing)                      │ │
│  │  • NumPy (numerical operations)                   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## 🔄 Data Pipeline (Detailed - Enhanced v2)

### Phase 1: Image Acquisition
- **Component**: `CameraCapture.js` (React)
- **Input**: Live video stream from device camera
- **Output**: JPEG blob at 0.95 quality
- **Key Points**:
  - Uses `getUserMedia()` with `facingMode: 'environment'`
  - Draws frame to Canvas element
  - Captures single frame on user action
  - No image preprocessing on frontend

### Phase 2: Fixed ROI Extraction
- **Component**: `ImageProcessor.crop_fixed_roi()`
- **Input**: Raw JPEG blob
- **Process**:
  1. Decode JPEG to numpy array (OpenCV)
  2. Center-crop to fixed dimensions (400x600px)
- **Output**: Cropped RGB image
- **Rationale**:
  - Fixed camera = predictable card position
  - No YOLO/object detection needed
  - O(1) operation with deterministic positioning

### Phase 3: Image Quality Assessment
- **Component**: `ImageQualityAnalyzer.assess_quality()`
- **Input**: Cropped card image (400x600)
- **Process**:
  1. **Brightness Score**: Normalized to optimal range (128 ± 128)
  2. **Contrast Score**: Standard deviation / 80 (max useful contrast)
  3. **Sharpness Score**: Laplacian variance / 500 (higher = sharper)
  4. **Motion Blur Score**: Edge density analysis (using Sobel)
  5. **Noise Score**: Median filter difference analysis
  6. **Composite Score**: Weighted average:
     - 30% sharpness (most important for OCR)
     - 25% contrast (text visibility)
     - 20% motion blur (stability indicator)
     - 15% brightness (lighting adequacy)
     - 10% noise (sensor quality)
- **Output**: Quality metrics dict + `is_acceptable` flag (threshold: 0.60)
- **Use Case**: Determines reliability of OCR and matching, triggers suggestions

### Phase 4: Card Name Extraction
- **Component**: `ImageProcessor.extract_name_region()` → `preprocess_for_ocr()` → `OCREngine.extract_card_name()`
- **Input**: Cropped card image
- **Process**:
  1. Extract top 80px (typical card name location)
  2. **Preprocessing**:
     - Grayscale conversion
     - Adaptive threshold (11x11 kernel, Gaussian C=2)
     - Morphological close (2x2 kernel) to connect broken text
     - Median blur (3x3) to reduce noise
     - **2x upscaling** for improved Tesseract accuracy
  3. Tesseract OCR with `--psm 6` (uniform block)
  4. Per-word confidence scoring (normalized 0-1)
- **Output**: (extracted_name, ocr_confidence)
- **Key Metrics**:
  - Confidence: Average per-word Tesseract confidence
  - Typical: >0.85 for well-lit, centered cards

### Phase 5: Card Code Extraction
- **Component**: `CardCodeExtractor.extract_and_validate()`
- **Input**: Cropped card image (400x600)
- **Process**:
  1. **ROI Extraction**: Bottom region (~60px from y=500)
     - Card codes typically printed at bottom
     - Small text requires specific handling
  2. **Aggressive Preprocessing** (more intensive than name):
     - **3x upscaling** (vs 2x for name) due to small text
     - **Larger adaptive threshold** (15x15 kernel vs 11x11)
     - **Stronger morphological ops** (3x3 kernel vs 2x2)
     - Targets small text clarity over large text
  3. **Pattern Validation**: Regex matching against known formats:
     ```python
     CARD_CODE_PATTERNS = [
       r'\b(\d{8}-\d+)\b',           # Passcode: 25345090-1
       r'\b([A-Z]{2,4}-\d{3,4})\b',  # Release: SDK-001
       r'\b([A-Z]{3,4})\s*-\s*(\d{3,4})\b',  # With space
     ]
     ```
  4. **Confidence Scoring**:
     - OCR confidence × 1.2 if pattern valid (reinforcement)
     - OCR confidence × 0.6 if pattern invalid (penalty)
- **Output**: {code, ocr_text, ocr_confidence, is_valid, confidence}
- **Why Separate OCR?**
  - Card codes use different font/size than name
  - Requires different preprocessing for small text
  - Pattern validation adds signal independent from OCR

### Phase 6: Card Matching
- **Component**: `CardMatcher.find_best_match()`
- **Input**: (extracted_name, name_ocr_confidence)
- **Process**:
  1. For each card in database (11,000+):
     - Calculate `token_sort_ratio(extracted_name, card_name)`
     - Token sort: "DRAGON WHITE EYES BLUE" matches "BLUE-EYES WHITE DRAGON"
     - Handles word reordering, punctuation, spacing
  2. Find card with highest fuzzy score
  3. Calculate fuzzy_confidence = fuzzy_score / 100
- **Output**: Matched card dict OR None
- **Fallback**: If no match above threshold, return top-5 candidates
- **Why FuzzyWuzzy?**
  - Robust to OCR errors (missing/extra chars)
  - Token sort handles formatting variations
  - More reliable than exact string matching

### Phase 7: Combined Confidence Scoring
- **Component**: Main `/identify_card` endpoint logic
- **Input**: All confidence signals from phases 3-6
- **Formula**:
  ```python
  combined_confidence = (
    0.30 × name_ocr_confidence +
    0.40 × fuzzy_match_confidence +
    0.15 × code_ocr_confidence +
    0.15 × image_quality_score
  )
  ```
- **Weighting Rationale**:
  - **40% Fuzzy Matching**: Most reliable signal
    - Validated against known database
    - Robust to OCR variations
  - **30% Name OCR**: Primary signal
    - Direct extraction from card
    - Highest signal-to-noise in good conditions
  - **15% Image Quality**: Reliability indicator
    - Affects all other signals
    - Lower quality = lower confidence in all results
  - **15% Card Code OCR**: Validation signal
    - Confirms card identity
    - Less critical than name but valuable for validation

### Phase 8: Result Generation & User Feedback
- **Component**: Response building logic
- **Needs Review Flag**: Set if ANY of:
  - combined_confidence < 0.80
  - code validation failed (is_valid = false)
  - image quality unacceptable (is_acceptable = false)
- **Suggestions Array**: Generated based on failures:
  - Sharpness < 0.5 → "Image is blurry. Try steady hand."
  - Brightness < 0.4 → "Image too dark. Increase lighting."
  - Brightness > 0.9 → "Image too bright. Reduce glare."
  - Noise < 0.5 → "Too much noise. Clean lens."
  - Code validation failed → "Card code not visible/readable."
  - Low confidence → "Try repositioning card."
- **Response Structure**:
  ```json
  {
    "success": true,
    "name": "...",
    "code": "...",
    "card_id": 12345,
    "confidence": 0.94,
    "source": "combined_pipeline",
    "needs_review": false,
    "suggestions": [],
    "metrics": {
      "name_ocr": 0.92,
      "code_ocr": 0.88,
      "fuzzy_match": 0.96,
      "image_quality": 0.91,
      "quality_breakdown": {...}
    },
    "extracted_text": {"name": "...", "code": "..."},
    ...card_details
  }
  ```

## 🗄️ Data Models

### Input: Image Blob
```javascript
// From Canvas.toBlob()
{
  type: 'image/jpeg',
  size: 50000,  // ~50KB for typical card photo
  data: ArrayBuffer
}
```

### Processing: ImageProcessor Output
```python
# numpy.ndarray
shape = (600, 400)  # height, width after 2x upscale
dtype = uint8      # values 0-255
```

### Matching: Card Database (from YGOPRODeck)
```json
{
  "id": 1234567,
  "name": "Blue-Eyes White Dragon",
  "type": "Synchro/Effect Monster",
  "atk": 3000,
  "def": 2500,
  "level": 8,
  "attribute": "LIGHT",
  "race": "Dragon",
  "desc": "2 Tuner monsters...",
  "archetype": "Blue-Eyes",
  "card_images": [
    {
      "image_url": "https://...",
      "image_url_small": "https://..."
    }
  ]
}
```

### Output: Identification Result
```json
{
  "success": true,
  "name": "Blue-Eyes White Dragon",
  "type": "Synchro/Effect Monster",
  "confidence": 0.95,
  "ocr_confidence": 0.92,
  "fuzzy_confidence": 0.97,
  "match_score": 98,
  "atk": 3000,
  "def": 2500,
  "level": 8,
  "attribute": "LIGHT",
  "race": "Dragon",
  "description": "...",
  "image_url": "https://...",
  "extracted_name": "BLUE EYES WHITE DRAGON"
}
```

## 🎯 Why Fixed Camera Simplifies the Problem

### Traditional Approach (Mobile App with Object Detection)
- ❌ Need YOLO/Faster R-CNN for card detection
- ❌ Handle variable distances (1-3 feet away)
- ❌ Handle rotation angles (-45° to +45°)
- ❌ Handle card occlusion
- ❌ 300-500ms inference time on mobile
- ❌ Large model (100MB+)
- ❌ Needs training data and annotation

### Fixed Camera Approach (MVP)
- ✅ Camera mounted on fixed 3D rig
- ✅ Constant distance (2 feet)
- ✅ Fixed angle (0°)
- ✅ Controlled placement area
- ✅ No detection needed - just crop ROI
- ✅ <100ms preprocessing
- ✅ Model-agnostic (works with any OCR)
- ✅ Zero training data needed

**Tradeoff**: Reduces portability BUT enables fast MVP iteration.

## 🗄️ Card Database Strategy

### YGOPRODeck API
- **Endpoint**: `https://db.ygoprodeck.com/api/v7/cardinfo.php`
- **Response**: ~11,000 cards in JSON
- **Size**: ~10-15MB
- **Format**: Array of card objects with full metadata

### Local Caching
- **File**: `backend/cache/cards_cache.json`
- **Format**: JSON with timestamp
- **Expiry**: 24 hours (configurable)
- **Benefits**:
  - First load downloads from API (~2-3s)
  - Subsequent loads use cache (<100ms)
  - Works offline after first fetch
  - Reduces load on YGOPRODeck servers

### Cache Structure
```json
{
  "timestamp": "2024-01-15T10:30:00.000000",
  "cards": [
    { ... },
    { ... }
  ]
}
```

## 📊 Confidence Scoring Rationale

### Why Not Pure Fuzzy Matching?
- Fuzzy matching alone fails for poorly scanned cards
- OCR provides direct text extraction signal
- But OCR can be unreliable with lighting/angle variations

### Why Not Pure OCR Confidence?
- Tesseract confidence calibration is inconsistent
- May report high confidence on garbage text
- Fuzzy matching validates against known card names

### Hybrid Approach
```
combined_confidence = 0.4 * ocr_conf + 0.6 * fuzzy_conf
```

- **40% weight to OCR**: Primary signal (direct extraction)
- **60% weight to Fuzzy**: Validation & robustness
- **Threshold**: 0.75 minimum (tunable in config)
- **Results**:
  - High accuracy on well-scanned cards
  - Graceful degradation with poor OCR
  - Shows candidates when confidence too low

## 🚀 Performance Characteristics

### Timing Breakdown (Target: <500ms)

| Phase | Time | Notes |
|-------|------|-------|
| Image decode | 20ms | JPEG → numpy array |
| ROI crop | 5ms | Simple array slicing |
| Preprocessing | 50ms | Threshold, morphology, upscale |
| OCR | 200ms | Tesseract (bottleneck) |
| Matching | 100ms | Loop through 11k cards with fuzzy |
| API response | 50ms | JSON serialization |
| **Total** | **425ms** | Plus network latency |

### Memory Usage
- Image (400x600): ~1.4MB
- Preprocessed (800x1200): ~3MB
- Card database (loaded): ~15MB
- **Total**: ~20MB footprint

## 🔐 Error Handling Strategy

### Network Errors
- Backend unreachable → Frontend shows "Backend Offline"
- API fetch fails → Use stale cache (if available)
- Fallback: Show empty state with retry option

### Image Errors
- Invalid image file → 400 Bad Request
- Empty image → 400 Bad Request
- Corrupt JPEG → cv2.imdecode returns None

### OCR Errors
- No text detected → "Could not extract card name"
- Very low confidence → Show candidates instead of error
- Tesseract crash → Try/catch, log error, return 500

### Matching Errors
- No cards loaded → 500 Internal Server Error
- No matching candidates → Return top-N fuzzy matches

## 🛠️ Technology Trade-offs

### FastAPI vs Django
- ✅ FastAPI: Faster, async support, auto Swagger UI, lighter weight
- ❌ Django: More batteries included but overkill for this MVP

### Tesseract vs ML Models
- ✅ Tesseract: Fast, reliable, no training, small footprint
- ❌ Cloud ML: Network latency, cost, privacy concerns
- ❌ TensorFlow: Slower on CPU, needs training data

### FuzzyWuzzy vs Levenshtein
- ✅ FuzzyWuzzy: Token sort ratio handles word order
- ❌ Levenshtein: Character-level, doesn't handle reordering

### React vs Vue/Angular
- ✅ React: Largest ecosystem, camera/Canvas libraries mature
- ❌ Vue: Smaller community for media APIs

### Tailwind vs Bootstrap
- ✅ Tailwind: Utility-first, smaller bundle, mobile-first
- ❌ Bootstrap: Heavier, more prescriptive

## 📱 Stage 2: Mobile Migration Plan

### Architecture Change
```
Browser (React)          →    React Native / Flutter
Backend (FastAPI)        →    Native Swift/Kotlin code
Tesseract OCR (Python)   →    TensorFlow Lite / ONNX model
YGOPRODeck API           →    Bundled SQLite database
Card Cache               →    Device storage (SQLite)
```

### Model Export Strategy
1. **Train lightweight OCR model**
   - Use Tesseract outputs as labels
   - Consider: PaddleOCR or MobileNet-based CNN
   - Train on ~1000 crop samples

2. **Export to TensorFlow Lite**
   ```python
   # Python training
   model = create_model()
   converter = tf.lite.TFLiteConverter.from_keras_model(model)
   tflite_model = converter.convert()
   
   # Save for mobile deployment
   with open('model.tflite', 'wb') as f:
       f.write(tflite_model)
   ```

3. **Integrate into App**
   - iOS: Use Core ML or TensorFlow Lite Swift
   - Android: Use TensorFlow Lite Android
   - Performance: <300ms on modern devices

### Database Strategy
- Precompile 11k cards to SQLite
- Include in app bundle (~20MB)
- Synchronize periodically (optional)
- Queries: FTS (Full Text Search) on card names

### Inference Pipeline
```
Camera Input
    ↓
Fixed ROI Crop (100ms)
    ↓
Preprocess (50ms)
    ↓
TFLite Inference (50-100ms)
    ↓
Fuzzy Match in SQLite (50ms)
    ↓
Display Result (200ms total)
```

## 🔍 Future Enhancements

### Batch Processing
- Scan multiple cards in single image
- Return array of identifications
- Handle card overlaps

### AR Overlay
- Display card info over live camera
- Augment reality with deck info
- Real-time identification (<100ms)

### User Accounts
- Save scan history
- Create deck lists
- Cloud sync

### Multi-Language
- International card names
- Support other TCGs (Magic, Pokémon)
- Transliteration support

### Computer Vision Improvements
- Perspective correction (handle tilted cards)
- Auto-detect card boundaries
- Lighting normalization

## 📋 Testing Strategy

### Unit Tests
- `test_image_processor.py`: ROI crop, preprocessing
- `test_ocr_engine.py`: Tesseract wrapper
- `test_card_matcher.py`: Fuzzy matching logic
- `test_card_cache.py`: API + cache logic

### Integration Tests
- POST /identify_card with real images
- Cache refresh workflow
- Error handling paths

### E2E Tests
- Frontend camera capture
- Full pipeline end-to-end
- Result verification

### Performance Tests
- <500ms target validation
- Memory profiling
- Cache hit rate monitoring

## 🚀 Deployment

### Backend Deployment (Production)
```bash
# Using Gunicorn + Nginx
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Or Docker
docker build -t yugioh-identifier-backend .
docker run -p 8000:8000 yugioh-identifier-backend
```

### Frontend Deployment (Production)
```bash
# Build optimized bundle
npm run build
# Deploy to Netlify, Vercel, or S3

# Or serve locally with nginx
```

### Environment Variables
```bash
# Backend (.env)
TESSERACT_PATH=/usr/bin/tesseract
CACHE_EXPIRY_HOURS=24
MIN_CONFIDENCE=0.75
FUZZY_MATCH_THRESHOLD=80
```

## 📚 References

- [YGOPRODeck API](https://db.ygoprodeck.com/api-guide/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy)
- [OpenCV Docs](https://docs.opencv.org/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)

---

**Last Updated**: January 2024  
**Author**: Senior Full-Stack Engineer  
**Status**: Production Ready (MVP)
