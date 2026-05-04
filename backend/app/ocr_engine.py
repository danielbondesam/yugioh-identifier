"""OCR engine using Tesseract."""

import pytesseract
import cv2
import numpy as np
from typing import List, Tuple
from app.config import TESSERACT_PATH, OCR_LANGUAGE


class OCREngine:
    """Handles text extraction from images using Tesseract."""

    def __init__(self):
        """Initialize Tesseract configuration."""
        pytesseract.pytesseract.pytesseract_cmd = TESSERACT_PATH

    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image: Preprocessed image
            
        Returns:
            Extracted text
        """
        try:
            text = pytesseract.image_to_string(
                image,
                lang=OCR_LANGUAGE,
                config='--psm 6'  # Single uniform block of text
            )
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def extract_card_name(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Extract card name from image with confidence estimation.
        
        Args:
            image: Preprocessed card name region
            
        Returns:
            Tuple of (extracted_name, confidence_score)
        """
        try:
            # Get OCR data with confidence
            data = pytesseract.image_to_data(
                image,
                lang=OCR_LANGUAGE,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = np.mean(confidences) / 100 if confidences else 0.5
            
            # Get full text
            text = pytesseract.image_to_string(image, lang=OCR_LANGUAGE, config='--psm 6').strip()
            
            return text, avg_confidence
        except Exception as e:
            print(f"OCR Error: {e}")
            return "", 0.0

    def get_ocr_confidence(self, image: np.ndarray) -> float:
        """
        Get overall OCR confidence score for an image.
        
        Args:
            image: Image to analyze
            
        Returns:
            Confidence score (0-1)
        """
        try:
            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT
            )
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            if confidences:
                return np.mean(confidences) / 100
            return 0.5
        except Exception:
            return 0.0
