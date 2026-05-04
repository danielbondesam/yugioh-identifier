"""
Quick testing script for the backend pipeline.

Usage:
    python test_pipeline.py                  # Test with generated test images
    python test_pipeline.py path/to/image.jpg  # Test with real image
"""

import sys
import argparse
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.dev_tools import MockCardGenerator, DataPipelineTester


def main():
    parser = argparse.ArgumentParser(description="Test YuGiOh identifier pipeline")
    parser.add_argument(
        "image",
        nargs="?",
        help="Path to test image (or generate synthetic test)"
    )
    args = parser.parse_args()

    tester = DataPipelineTester()

    if args.image:
        # Test with provided image
        print(f"Testing with image: {args.image}")
        if not Path(args.image).exists():
            print(f"Error: Image not found: {args.image}")
            sys.exit(1)
        
        results = tester.test_pipeline(args.image)
        tester.print_results(results)
    else:
        # Generate test images
        print("Generating test card images...")
        
        test_cards = [
            "Blue Eyes White Dragon",
            "Dark Magician",
            "Red Eyes Black Dragon",
        ]
        
        gen = MockCardGenerator()
        
        for card_name in test_cards:
            print(f"\nTesting: {card_name}")
            
            # Generate image
            image = gen.create_test_card_image(card_name)
            image_path = f"/tmp/test_{card_name.replace(' ', '_')}.jpg"
            gen.save_test_image(image, image_path)
            
            # Test pipeline
            results = tester.test_pipeline(image_path)
            tester.print_results(results)


if __name__ == "__main__":
    main()
