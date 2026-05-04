"""Image preprocessing for OCR optimization."""

import cv2
import numpy as np
from PIL import ImageEnhance, Image
from typing import Tuple


class ImageProcessor:
    """Handles image preprocessing for improved OCR accuracy."""

    @staticmethod
    def crop_fixed_roi(image: np.ndarray, width: int = 400, height: int = 600) -> np.ndarray:
        """
        Crop fixed Region of Interest from image.
        
        Assumes fixed camera placement - crops center of image.
        
        Args:
            image: Input image array
            width: ROI width
            height: ROI height
            
        Returns:
            Cropped image array
        """
        h, w = image.shape[:2]
        
        # Center crop
        x_start = max(0, (w - width) // 2)
        y_start = max(0, (h - height) // 2)
        x_end = min(w, x_start + width)
        y_end = min(h, y_start + height)
        
        return image[y_start:y_end, x_start:x_end]

    @staticmethod
    def extract_name_region(image: np.ndarray, region_height: int = 80) -> np.ndarray:
        """
        Extract top region of card (typically contains name).
        
        Args:
            image: Cropped card image
            region_height: Height of name region
            
        Returns:
            Top region of image
        """
        return image[:region_height, :]

    @staticmethod
    def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for Tesseract OCR.
        
        Pipeline:
        1. Grayscale
        2. Adaptive threshold
        3. Contrast enhancement
        4. Denoising
        5. Upscaling
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale if color
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Adaptive threshold for better text separation
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2
        )

        # Denoise
        denoised = cv2.medianBlur(thresh, 3)

        # Morph operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)

        # Upscale 2x for better OCR accuracy
        processed = cv2.resize(
            processed,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        return processed

    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast using PIL for additional clarity.
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(1.5)
        return np.array(enhanced)

    @staticmethod
    def sharpen(image: np.ndarray) -> np.ndarray:
        """
        Sharpen image to enhance text edges.
        
        Args:
            image: Input image
            
        Returns:
            Sharpened image
        """
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened
