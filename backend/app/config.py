"""Configuration and constants for the backend."""

import os
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Image processing
FIXED_ROI_WIDTH = 400
FIXED_ROI_HEIGHT = 600
CARD_NAME_ROI_HEIGHT = 80  # Top portion for name extraction
CARD_CODE_ROI_TOP = 500  # Y position where card code typically starts
CARD_CODE_ROI_HEIGHT = 60  # Height of code region
CARD_CODE_ROI_WIDTH = 400  # Width should match card width

# OCR configuration
OCR_LANGUAGE = "eng"
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Image Quality configuration
IMAGE_QUALITY_THRESHOLD = 0.50  # Minimum acceptable image quality (0-1)
# Lowered from 0.60 to improve tolerance for low-light conditions

# API configuration
YGOPRODECK_API_BASE = "https://db.ygoprodeck.com/api/v7"
CARD_CACHE_FILE = CACHE_DIR / "cards_cache.json"
CACHE_EXPIRY_HOURS = 24

# Matching configuration
FUZZY_MATCH_THRESHOLD = 70  # Lowered from 80 for improved low-light tolerance
MIN_CONFIDENCE = 0.65  # Lowered from 0.75 to accept cards with lower confidence

# Confidence weighting for combined score
# name_ocr_weight + code_ocr_weight + fuzzy_weight + quality_weight = 1.0
NAME_OCR_WEIGHT = 0.30
CODE_OCR_WEIGHT = 0.15
FUZZY_MATCH_WEIGHT = 0.40
IMAGE_QUALITY_WEIGHT = 0.15
