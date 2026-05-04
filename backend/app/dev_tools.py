"""Development and testing utilities."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.card_cache import CardCache
from app.image_processor import ImageProcessor
from app.ocr_engine import OCREngine
from app.card_matcher import CardMatcher
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json


class MockCardGenerator:
    """Generate test cards and images for development."""

    @staticmethod
    def create_test_card_image(card_name: str, width: int = 400, height: int = 600) -> np.ndarray:
        """
        Create a simple test card image with text.
        
        Args:
            card_name: Name to write on card
            width: Card width
            height: Card height
            
        Returns:
            numpy array (OpenCV format)
        """
        # Create white background
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a decent font, fall back to default
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Add card name
        bbox = draw.textbbox((0, 0), card_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = 50
        
        draw.text((x, y), card_name, fill='black', font=font)
        
        # Add border
        border_color = 'red'
        draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)
        
        # Convert to numpy array (OpenCV format)
        image_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return image_array

    @staticmethod
    def save_test_image(image: np.ndarray, filename: str) -> str:
        """Save test image to file."""
        cv2.imwrite(filename, image)
        return filename


class DataPipelineTester:
    """Test the complete identification pipeline."""

    def __init__(self):
        """Initialize components."""
        self.processor = ImageProcessor()
        self.ocr = OCREngine()
        self.cards = CardCache.get_cards()
        self.matcher = CardMatcher(self.cards)

    def test_pipeline(self, image_path: str) -> dict:
        """
        Test complete pipeline on an image.
        
        Args:
            image_path: Path to test image
            
        Returns:
            Result dictionary with timing info
        """
        import time
        
        start = time.time()
        
        # Load image
        image = cv2.imread(image_path)
        t1 = time.time()
        
        # Crop ROI
        roi = self.processor.crop_fixed_roi(image)
        t2 = time.time()
        
        # Extract name region
        name_region = self.processor.extract_name_region(roi)
        t3 = time.time()
        
        # Preprocess
        preprocessed = self.processor.preprocess_for_ocr(name_region)
        t4 = time.time()
        
        # OCR
        text, confidence = self.ocr.extract_card_name(preprocessed)
        t5 = time.time()
        
        # Match
        result = self.matcher.find_best_match(text, confidence)
        candidates = self.matcher.find_top_n_matches(text, confidence, n=5)
        t6 = time.time()
        
        return {
            "extracted_text": text,
            "ocr_confidence": confidence,
            "match_result": result,
            "candidates": candidates,
            "timing": {
                "load_image": t1 - start,
                "crop_roi": t2 - t1,
                "extract_region": t3 - t2,
                "preprocess": t4 - t3,
                "ocr": t5 - t4,
                "matching": t6 - t5,
                "total": t6 - start
            }
        }

    def print_results(self, results: dict):
        """Pretty print results."""
        print("\n" + "="*60)
        print("PIPELINE TEST RESULTS")
        print("="*60)
        
        print(f"\n📝 Extracted Text: {results['extracted_text']}")
        print(f"📊 OCR Confidence: {results['ocr_confidence']:.2%}")
        
        if results['match_result']:
            card = results['match_result']
            print(f"\n✅ MATCH FOUND: {card['name']}")
            print(f"   Type: {card.get('type', 'N/A')}")
            print(f"   Combined Confidence: {card.get('confidence', 0):.2%}")
            print(f"   Match Score: {card.get('match_score', 0)}")
        else:
            print(f"\n⚠️  No exact match found. Top candidates:")
            for i, card in enumerate(results['candidates'], 1):
                print(f"   {i}. {card['name']} ({card.get('confidence', 0):.2%})")
        
        print("\n⏱️  Timing Breakdown:")
        for key, value in results['timing'].items():
            if key != 'total':
                print(f"   {key:.<20} {value*1000:>6.1f}ms")
        print(f"   {'TOTAL':.<20} {results['timing']['total']*1000:>6.1f}ms")
        print("="*60 + "\n")


if __name__ == "__main__":
    print("Yu-Gi-Oh Identifier - Development Tools")
    print("Import this module to use development utilities")
