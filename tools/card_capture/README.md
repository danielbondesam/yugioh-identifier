# Card Capture Dataset Tool

Simple OpenCV-based camera capture utility for collecting Yu-Gi-Oh card images.

**This tool is NOT the main scanner.** It's a standalone dataset collection utility to help debug the OCR and matching pipeline.

## Purpose

The main scanner may fail to identify cards due to issues in:
- OCR preprocessing and extraction
- ROI (Region of Interest) detection
- Fuzzy matching logic
- Image quality assessment

This tool captures real card images without running the scanner pipeline, allowing you to:
1. Build a local test dataset
2. Test preprocessing independently
3. Debug OCR extraction
4. Validate fuzzy matching logic
5. Analyze image quality metrics

## Setup

### Windows Installation

1. **Install Python** (if not already installed):
   - Download from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Install OpenCV**:
   ```bash
   cd tools\card_capture
   pip install -r requirements.txt
   ```

3. **Connect USB camera**:
   - Plug in your USB camera
   - Verify it appears in device manager

## Usage

### Basic Capture

```bash
cd tools\card_capture
python capture_cards.py --camera 0
```

### With Card Label

```bash
python capture_cards.py --camera 0 --label blue_eyes_white_dragon
python capture_cards.py --camera 0 --label hazy_flame_hyppogriff
```

### Test Camera Index

If default camera (0) doesn't work:

```bash
python capture_cards.py --camera 1
python capture_cards.py --camera 2
```

### With ROI Cropping

Capture both full frame and cropped ROI (Region of Interest):

```bash
# Use default ROI (50, 50, 400, 600)
python capture_cards.py --camera 0 --label test_card --show-roi

# Use custom ROI (x, y, width, height)
python capture_cards.py --camera 0 --label test_card --roi 50 50 400 600
```

### Custom Resolution

```bash
python capture_cards.py --camera 0 --width 1920 --height 1080
```

### All Options

```bash
python capture_cards.py --help
```

## Keyboard Controls in Preview Window

| Key      | Action                |
|----------|----------------------|
| **SPACE** | Capture image       |
| **Q**    | Quit                |
| **ESC**  | Quit                |
| **R**    | Reset counter       |
| **C**    | Change camera index |
| **H**    | Toggle help overlay |

## Output Structure

```
data/
└── captured_cards/
    ├── raw/
    │   ├── 20260505_153012_unknown_001.jpg
    │   ├── 20260505_153045_blue_eyes_001.jpg
    │   └── ...
    ├── roi/                    (if --roi or --show-roi)
    │   ├── 20260505_153045_blue_eyes_001_roi.jpg
    │   └── ...
    └── metadata.csv
```

## Metadata File

The tool automatically logs captured images to `metadata.csv`:

```csv
filename,roi_filename,label,camera_index,width,height,captured_at,notes
20260505_153012_unknown_001.jpg,,unknown,0,1280,720,2026-05-05T15:30:12.123456,
20260505_153045_blue_eyes_001.jpg,20260505_153045_blue_eyes_001_roi.jpg,blue_eyes,0,1280,720,2026-05-05T15:30:45.654321,
```

## Workflow: Using Captured Images for Debugging

### Step 1: Capture Dataset

```bash
python capture_cards.py --camera 0 --label my_test_card
```

Capture 5-10 images under different lighting conditions.

### Step 2: Test Preprocessing

Use a standalone preprocessing script (in backend) to examine:
- Image quality metrics (brightness, contrast, sharpness)
- OCR confidence on extracted text
- What text Tesseract actually reads

```bash
cd backend
python -c "
import cv2
from app.image_processor import ImageProcessor
from app.image_quality import ImageQualityAnalyzer

img = cv2.imread('../data/captured_cards/raw/20260505_153012_unknown_001.jpg')
quality = ImageQualityAnalyzer.assess_quality(img)
print('Quality:', quality)

preprocessed = ImageProcessor.preprocess_for_ocr(img)
cv2.imwrite('debug_preprocessed.jpg', preprocessed)
"
```

### Step 3: Test OCR Extraction

Check what text Tesseract extracts:

```bash
python -c "
import cv2
import pytesseract
from app.image_processor import ImageProcessor

img = cv2.imread('../data/captured_cards/raw/20260505_153012_unknown_001.jpg')
cropped = img[:80, :]  # Top region (name)
preprocessed = ImageProcessor.preprocess_for_ocr(cropped)
text = pytesseract.image_to_string(preprocessed)
print('Extracted:', text)
"
```

### Step 4: Test Fuzzy Matching

Check if extracted text fuzzy matches known card names:

```bash
python -c "
from app.card_matcher import CardMatcher
from app.card_cache import CardCache

cards = CardCache.get_cards()
matcher = CardMatcher(cards)

# Test different text variations
test_names = [
    'Blue Eyes White Dragon',
    'Blue-Eyes White Dragon',
    'BLUE EYES WHITE DRAGON',
]

for name in test_names:
    result = matcher.find_best_match(name, 0.8)
    print(f'{name} -> {result[\"name\"] if result else \"No match\"}')"
```

### Step 5: Validate Full Pipeline

Once you understand individual components, test the full `/identify_card` endpoint:

```bash
# Start backend server
cd backend
uvicorn app.main:app --reload

# In another terminal, test with captured image
python -c "
import requests
import cv2

img = cv2.imread('../data/captured_cards/raw/20260505_153012_unknown_001.jpg')
_, buffer = cv2.imencode('.jpg', img)

response = requests.post(
    'http://localhost:8000/identify_card',
    files={'image': buffer.tobytes()}
)
print(response.json())
"
```

## Troubleshooting

### Camera Not Found

- **Try different index:**
  ```bash
  python capture_cards.py --camera 1
  python capture_cards.py --camera 2
  python capture_cards.py --camera 3
  ```

- **Check Device Manager:**
  - Right-click Start → Device Manager
  - Look for "Cameras" or "Image Devices"
  - Note the camera name/index

- **Camera in use by another app:**
  - Close other applications using the camera (Teams, Zoom, browsers with webcam access)
  - Kill camera processes: `taskkill /F /IM camera.exe`

### Black or Dark Preview

- Check lighting in capture area
- Adjust preview window brightness (camera settings)
- Try different camera index
- Ensure lens is not covered

### Preview Window Won't Open

- Make sure you have a display/monitor connected
- Try headless mode (not applicable here, but good to know for automation)

### Slow Frame Rate

- Lower resolution: `--width 640 --height 480`
- Use a better USB cable (current draw)
- Close other CPU-intensive applications

### File Save Permission Error

- Ensure `data/` directory is writable
- Run PowerShell as Administrator if needed
- Check antivirus is not blocking file writes

## Integration with Main Scanner

Once you have a dataset:

1. **Copy images to test folder:**
   ```bash
   cp data/captured_cards/raw/* ../backend/tests/images/
   ```

2. **Create a test batch script** to run full pipeline on dataset

3. **Compare results** before/after preprocessing changes

4. **Track improvements** using metadata.csv

## Tips for Good Captures

1. **Use consistent lighting** - avoid shadows and glare
2. **Keep card steady** - use a mount or holder if available
3. **Fill most of frame** - maximize card size in image
4. **Capture multiple angles** - helps test robustness
5. **Test edge cases** - damaged cards, worn text, poor lighting
6. **Label consistently** - helps organize dataset for analysis

## Example Session

```bash
PS> cd .\tools\card_capture\
PS> python capture_cards.py --camera 0 --label test_session_001

============================================================
Card Capture Tool
============================================================
Camera Index: 0
Label: test_session_001
Output: data/captured_cards/raw
ROI: None

Press H for help, SPACE to capture, Q to quit
============================================================

✓ Connected to camera 0
✓ Saved: 20260505_153012_test_session_001_001.jpg
✓ Saved: 20260505_153015_test_session_001_002.jpg
✓ Saved: 20260505_153018_test_session_001_003.jpg

👋 Exiting...

============================================================
Session Summary
============================================================
Total images captured: 3
Output folder: data\captured_cards\raw
Metadata file: data\captured_cards\metadata.csv
============================================================
```

## Next Steps

- Use captured images to test preprocessing and OCR
- Identify bottlenecks in the scanner pipeline
- Create targeted fixes for specific OCR or matching issues
- Build a regression test suite with your dataset

---

**For more information about the main scanner, see [../../../README.md](../../../README.md)**
