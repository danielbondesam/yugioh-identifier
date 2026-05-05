"""Card code extraction from Yu-Gi-Oh card images."""

import re
import cv2
import numpy as np
import pytesseract
from typing import Tuple, Optional
from app.config import TESSERACT_PATH, OCR_LANGUAGE


class CardCodeExtractor:
    """Handles extraction and validation of Yu-Gi-Oh card codes."""

    # Yu-Gi-Oh card code patterns:
    # Format: XX-XXXX[A-Z]-[0-9]{4}
    # Examples: 25345090-1, SDK-001, 25345090-1, etc.
    # Common formats:
    # - XXXXXXXX-X (8 digits hyphen digit) - Passcode format
    # - XXX-XXX (3 digits hyphen 3 digits) - Release format
    CARD_CODE_PATTERNS = [
        r'\b(\d{8}-\d+)\b',  # Passcode: 25345090-1, 25345090-2, etc.
        r'\b([A-Z]{2,4}-\d{3,4})\b',  # Release code: SDK-001, LOB-001, etc.
        r'\b([A-Z]{3,4})\s*-\s*(\d{3,4})\b',  # With space: SDK - 001
        r'\b(\d{1,4})\b(?=[^0-9]|$)',  # Solo card number (less reliable)
    ]

    def __init__(self):
        """Initialize Tesseract configuration."""
        pytesseract.pytesseract.pytesseract_cmd = TESSERACT_PATH

    @staticmethod
    def extract_code_region(
        card_image: np.ndarray,
        code_roi_top: int = 500,
        code_roi_height: int = 60,
        code_roi_width: int = 400
    ) -> np.ndarray:
        """
        Extract the card code region from card image.

        Yu-Gi-Oh cards typically have code at bottom of card.

        Args:
            card_image: Cropped card image (400x600)
            code_roi_top: Y position to start extracting (from top)
            code_roi_height: Height of code region
            code_roi_width: Width of code region (should match card width)

        Returns:
            Cropped code region
        """
        h, w = card_image.shape[:2]

        # Ensure bounds are valid
        y_start = max(0, min(code_roi_top, h - code_roi_height))
        y_end = min(h, y_start + code_roi_height)
        x_start = max(0, (w - code_roi_width) // 2)
        x_end = min(w, x_start + code_roi_width)

        return card_image[y_start:y_end, x_start:x_end]

    @staticmethod
    def preprocess_for_code_ocr(
        image: np.ndarray,
        upscale_factor: int = None
    ) -> np.ndarray:
        """
        Preprocess image specifically for small card code text.

        Card codes are small text, so we need aggressive preprocessing:
        - Higher upscaling for small text
        - Aggressive contrast enhancement
        - Morphological operations to clean noise

        Args:
            image: Input image region
            upscale_factor: Override upscale factor (None = auto-detect)

        Returns:
            Preprocessed image
        """
        # Convert to grayscale if color
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Auto-detect upscale factor based on image size
        if upscale_factor is None:
            h, w = gray.shape[:2]
            # For small images, use even more aggressive upscaling
            if w < 300:
                upscale_factor = 5
            elif w < 600:
                upscale_factor = 4
            else:
                upscale_factor = 3

        # CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Aggressive upscaling first for small text
        upscaled = cv2.resize(
            enhanced,
            None,
            fx=upscale_factor,
            fy=upscale_factor,
            interpolation=cv2.INTER_CUBIC
        )

        # Otsu thresholding for small text
        _, thresh = cv2.threshold(
            upscaled, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Morphological close to connect broken characters
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Denoise
        denoised = cv2.medianBlur(processed, 3)

        return denoised

    def extract_card_code(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Extract card code from preprocessed image region.

        Args:
            image: Preprocessed card code region

        Returns:
            Tuple of (extracted_code, confidence_score)
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
            text = pytesseract.image_to_string(
                image,
                lang=OCR_LANGUAGE,
                config='--psm 6'
            ).strip()

            if not text:
                return None, 0.0

            return text, avg_confidence

        except Exception as e:
            print(f"Card code OCR error: {e}")
            return None, 0.0

    def validate_card_code(self, code_text: str) -> Tuple[Optional[str], bool]:
        """
        Validate extracted text against known Yu-Gi-Oh card code patterns.

        Args:
            code_text: Extracted text from OCR

        Returns:
            Tuple of (validated_code, is_valid)
        """
        if not code_text:
            return None, False

        # Remove whitespace and normalize
        normalized = code_text.strip().upper()

        # Try each pattern
        for pattern in self.CARD_CODE_PATTERNS:
            match = re.search(pattern, normalized)
            if match:
                extracted_code = match.group(1) if match.lastindex else match.group(0)
                return extracted_code, True

        return None, False

    def extract_and_validate(
        self,
        card_image: np.ndarray,
        code_roi_top: int = 500,
        code_roi_height: int = 60,
        code_roi_width: int = 400
    ) -> dict:
        """
        Complete pipeline for extracting and validating card code.

        Args:
            card_image: Full cropped card image (400x600)
            code_roi_top: Y position for code region
            code_roi_height: Height of code region
            code_roi_width: Width of code region

        Returns:
            Dict with:
                - code: Extracted and validated code (or None)
                - ocr_text: Raw OCR output
                - ocr_confidence: OCR confidence score
                - is_valid: Whether code matches known patterns
                - confidence: Combined confidence score
        """
        # Extract code region
        code_region = self.extract_code_region(
            card_image,
            code_roi_top=code_roi_top,
            code_roi_height=code_roi_height,
            code_roi_width=code_roi_width
        )

        # Preprocess for OCR
        preprocessed = self.preprocess_for_code_ocr(code_region)

        # Extract text via OCR
        ocr_text, ocr_confidence = self.extract_card_code(preprocessed)

        # Validate against patterns
        validated_code, is_valid = self.validate_card_code(ocr_text or "")

        # Combine confidences
        # If validation passes, increase confidence score
        combined_confidence = ocr_confidence * (1.2 if is_valid else 0.6)
        combined_confidence = min(1.0, combined_confidence)

        return {
            "code": validated_code,
            "ocr_text": ocr_text,
            "ocr_confidence": round(ocr_confidence, 3),
            "is_valid": is_valid,
            "confidence": round(combined_confidence, 3)
        }
