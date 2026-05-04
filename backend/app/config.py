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

# OCR configuration
OCR_LANGUAGE = "eng"
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# API configuration
YGOPRODECK_API_BASE = "https://db.ygoprodeck.com/api/v7"
CARD_CACHE_FILE = CACHE_DIR / "cards_cache.json"
CACHE_EXPIRY_HOURS = 24

# Matching configuration
FUZZY_MATCH_THRESHOLD = 80
MIN_CONFIDENCE = 0.75
