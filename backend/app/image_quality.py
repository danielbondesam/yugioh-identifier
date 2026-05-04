"""Image quality analysis for OCR reliability assessment."""

import cv2
import numpy as np
from typing import Tuple


class ImageQualityAnalyzer:
    """Analyzes image quality and provides scoring for OCR reliability."""

    # Quality thresholds
    MIN_BRIGHTNESS = 30
    MAX_BRIGHTNESS = 225
    MIN_CONTRAST = 20
    MIN_SHARPNESS = 100

    @staticmethod
    def calculate_brightness(image: np.ndarray) -> float:
        """
        Calculate average brightness of image.

        Args:
            image: Input image (grayscale or color)

        Returns:
            Average brightness value (0-255)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        return float(np.mean(gray))

    @staticmethod
    def calculate_contrast(image: np.ndarray) -> float:
        """
        Calculate contrast using standard deviation.

        Args:
            image: Input image (grayscale or color)

        Returns:
            Contrast score (0-255 scale)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        return float(np.std(gray))

    @staticmethod
    def calculate_sharpness(image: np.ndarray) -> float:
        """
        Calculate image sharpness using Laplacian variance.

        Higher values indicate sharper image.

        Args:
            image: Input image (grayscale or color)

        Returns:
            Sharpness score
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        return float(variance)

    @staticmethod
    def detect_motion_blur(image: np.ndarray) -> float:
        """
        Detect motion blur using edge detection.

        Args:
            image: Input image (grayscale or color)

        Returns:
            Motion blur score (0-1, lower = more blur)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Sobel edges
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        # Edge magnitude
        magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)
        edge_count = np.sum(magnitude > 50)

        # Normalize to 0-1
        total_pixels = gray.shape[0] * gray.shape[1]
        blur_score = min(1.0, float(edge_count) / (total_pixels / 100))

        return blur_score

    @staticmethod
    def detect_noise(image: np.ndarray) -> float:
        """
        Estimate noise level using high-frequency components.

        Args:
            image: Input image (grayscale or color)

        Returns:
            Noise score (0-1, lower = less noise)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply median filter
        median = cv2.medianBlur(gray, 5)

        # Difference indicates noise
        noise = np.abs(gray.astype(float) - median.astype(float))
        noise_level = float(np.mean(noise)) / 255.0

        return noise_level

    @classmethod
    def assess_quality(cls, image: np.ndarray) -> dict:
        """
        Comprehensive image quality assessment.

        Args:
            image: Input image (400x600 crop)

        Returns:
            Dict with:
                - brightness: 0-1 score
                - contrast: 0-1 score
                - sharpness: 0-1 score
                - motion_blur: 0-1 score
                - noise: 0-1 score
                - overall_quality: 0-1 composite score
                - is_acceptable: Whether image quality is acceptable
        """
        brightness = cls.calculate_brightness(image)
        contrast = cls.calculate_contrast(image)
        sharpness = cls.calculate_sharpness(image)
        motion_blur = cls.detect_motion_blur(image)
        noise = cls.detect_noise(image)

        # Normalize scores to 0-1
        brightness_score = max(0, min(1, 1.0 - abs(brightness - 128) / 128))
        contrast_score = max(0, min(1, contrast / 80))
        sharpness_score = max(0, min(1, sharpness / 500))
        motion_blur_score = motion_blur  # Already 0-1
        noise_score = max(0, 1.0 - noise)  # Invert: lower noise = higher score

        # Composite score with weights
        overall_quality = (
            brightness_score * 0.15 +
            contrast_score * 0.25 +
            sharpness_score * 0.30 +
            motion_blur_score * 0.20 +
            noise_score * 0.10
        )

        # Image is acceptable if quality is above 0.60
        is_acceptable = overall_quality >= 0.60

        return {
            "brightness": round(brightness_score, 3),
            "contrast": round(contrast_score, 3),
            "sharpness": round(sharpness_score, 3),
            "motion_blur": round(motion_blur_score, 3),
            "noise": round(noise_score, 3),
            "overall_quality": round(overall_quality, 3),
            "is_acceptable": is_acceptable
        }
