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
            width: ROI width (target)
            height: ROI height (target)
            
        Returns:
            Cropped image array (will be smaller if source image is small)
        """
        h, w = image.shape[:2]
        
        # If image is too small, use full image
        if w < width or h < height:
            return image
        
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
    def preprocess_for_ocr(image: np.ndarray, upscale_factor: int = None) -> np.ndarray:
        """
        Preprocess image for Tesseract OCR.
        
        Pipeline (optimized order for small text):
        1. Grayscale
        2. Upscale first (dynamic based on image size)
        3. CLAHE contrast enhancement
        4. Otsu thresholding for better text isolation
        5. Denoising
        
        NOTE: Upscaling BEFORE contrast enhancement produces better results
        than upscaling after, especially for small text.
        
        Args:
            image: Input image
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
            # For small images (< 300px width), use 4x upscaling
            # For medium (300-600px), use 3x
            # For large (> 600px), use 2x
            if w < 300:
                upscale_factor = 4
            elif w < 600:
                upscale_factor = 3
            else:
                upscale_factor = 2

        # UPSCALE FIRST - This is critical for small text recognition
        upscaled = cv2.resize(
            gray,
            None,
            fx=upscale_factor,
            fy=upscale_factor,
            interpolation=cv2.INTER_CUBIC
        )

        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # Better for card images with varying lighting
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(upscaled)

        # Otsu thresholding - automatically finds optimal threshold
        # Better than fixed/adaptive threshold for mixed text
        _, thresh = cv2.threshold(
            enhanced, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Denoise
        denoised = cv2.medianBlur(thresh, 3)

        return denoised

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
