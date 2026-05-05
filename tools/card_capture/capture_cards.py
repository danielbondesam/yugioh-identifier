#!/usr/bin/env python3
"""
Yu-Gi-Oh Card Dataset Capture Tool

Simple OpenCV-based camera capture utility for collecting card images.
This tool is NOT the main scanner - it's for building a test dataset.

Usage:
    python capture_cards.py --camera 0
    python capture_cards.py --camera 0 --label blue_eyes_white_dragon
    python capture_cards.py --camera 0 --label hazy_flame --show-roi
    python capture_cards.py --camera 0 --roi 50 50 400 600

Keyboard Controls:
    SPACE   - Capture image
    Q/ESC   - Quit
    R       - Reset counter
    H       - Show help
    C       - Change camera
"""

import cv2
import os
import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional


class CardCaptureUtility:
    """OpenCV-based camera capture for card dataset collection."""

    def __init__(
        self,
        camera_index: int = 0,
        label: str = "unknown",
        output_dir: str = None,
        width: int = 1280,
        height: int = 720,
        roi: Optional[Tuple[int, int, int, int]] = None,
        show_roi: bool = False,
    ):
        """
        Initialize capture utility.

        Args:
            camera_index: Camera device index
            label: Label prefix for captured images
            output_dir: Output directory (auto-created if needed)
            width: Capture width
            height: Capture height
            roi: ROI as (x, y, w, h) for cropping
            show_roi: Draw ROI rectangle on preview
        """
        self.camera_index = camera_index
        self.label = label
        self.show_roi = show_roi
        self.roi = roi
        self.width = width
        self.height = height
        self.counter = 0
        self.capture = None
        self.running = False

        # Setup output directories
        if output_dir is None:
            output_dir = "data/captured_cards"
        
        self.output_dir = Path(output_dir)
        self.raw_dir = self.output_dir / "raw"
        self.roi_dir = self.output_dir / "roi"
        self.metadata_file = self.output_dir / "metadata.csv"

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        if self.roi:
            self.roi_dir.mkdir(parents=True, exist_ok=True)

        # Initialize metadata CSV if not exists
        if not self.metadata_file.exists():
            with open(self.metadata_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'filename',
                    'roi_filename',
                    'label',
                    'camera_index',
                    'width',
                    'height',
                    'captured_at',
                    'notes'
                ])

    def connect_camera(self) -> bool:
        """
        Connect to camera device.

        Returns:
            True if successful, False otherwise
        """
        if self.capture is not None:
            self.capture.release()

        self.capture = cv2.VideoCapture(self.camera_index)
        
        if not self.capture.isOpened():
            print(f"❌ Failed to open camera {self.camera_index}")
            return False

        # Set resolution
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        print(f"✓ Connected to camera {self.camera_index}")
        return True

    def capture_image(self, frame: cv2.Mat) -> bool:
        """
        Capture and save image.

        Args:
            frame: Current frame from camera

        Returns:
            True if saved successfully
        """
        self.counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filename: YYYYMMDD_HHMMSS_<label>_<counter>.jpg
        filename = f"{timestamp}_{self.label}_{self.counter:03d}.jpg"
        filepath = self.raw_dir / filename

        # Save full frame
        if cv2.imwrite(str(filepath), frame):
            print(f"✓ Saved: {filename}")
        else:
            print(f"❌ Failed to save: {filename}")
            self.counter -= 1
            return False

        roi_filename = None
        
        # Save ROI if specified
        if self.roi:
            x, y, w, h = self.roi
            roi_frame = frame[y:y+h, x:x+w]
            roi_filename = f"{timestamp}_{self.label}_{self.counter:03d}_roi.jpg"
            roi_filepath = self.roi_dir / roi_filename
            
            if cv2.imwrite(str(roi_filepath), roi_frame):
                print(f"  └─ ROI saved: {roi_filename}")
            else:
                print(f"  └─ Failed to save ROI")
                roi_filename = None

        # Log to metadata CSV
        try:
            with open(self.metadata_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    filename,
                    roi_filename or '',
                    self.label,
                    self.camera_index,
                    frame.shape[1],  # width
                    frame.shape[0],  # height
                    datetime.now().isoformat(),
                    ''
                ])
        except Exception as e:
            print(f"⚠ Failed to log metadata: {e}")

        return True

    def show_help_overlay(self) -> str:
        """Return help text."""
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Card Capture Tool - Help
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPACE   Capture image
Q/ESC   Quit
R       Reset counter
C       Change camera
H       Hide help
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def draw_overlay(self, frame: cv2.Mat, show_help: bool = False) -> cv2.Mat:
        """
        Draw preview overlay with info.

        Args:
            frame: Input frame
            show_help: Show help overlay

        Returns:
            Frame with overlay
        """
        output = frame.copy()
        h, w = frame.shape[:2]

        # Semi-transparent background for overlay
        overlay = output.copy()
        cv2.rectangle(overlay, (10, 10), (400, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, output, 0.7, 0, output)

        # Text info
        y_pos = 35
        cv2.putText(output, f"Camera: {self.camera_index}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_pos += 30
        cv2.putText(output, f"Label: {self.label}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_pos += 30
        cv2.putText(output, f"Captured: {self.counter}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_pos += 30
        cv2.putText(output, f"Output: {self.raw_dir.name}/", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw ROI if specified
        if self.roi or self.show_roi:
            x, y, rw, rh = self.roi if self.roi else (50, 50, 400, 600)
            cv2.rectangle(output, (x, y), (x + rw, y + rh), (0, 255, 255), 2)
            cv2.putText(output, "ROI", (x + 5, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # Help overlay
        if show_help:
            help_text = self.show_help_overlay()
            y_pos = 200
            for line in help_text.split('\n'):
                if line.strip():
                    cv2.putText(output, line, (20, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    y_pos += 25

        # Control hint at bottom
        cv2.putText(output, "SPACE=Capture  Q=Quit  R=Reset  C=Camera  H=Help",
                   (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return output

    def run(self):
        """Run capture loop."""
        if not self.connect_camera():
            return False

        self.running = True
        show_help = False

        print(f"\n{'='*60}")
        print(f"Card Capture Tool")
        print(f"{'='*60}")
        print(f"Camera Index: {self.camera_index}")
        print(f"Label: {self.label}")
        print(f"Output: {self.raw_dir}")
        print(f"ROI: {self.roi if self.roi else 'None'}")
        print(f"\nPress H for help, SPACE to capture, Q to quit")
        print(f"{'='*60}\n")

        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                print("❌ Failed to read frame")
                break

            # Draw overlay
            display_frame = self.draw_overlay(frame, show_help)

            # Show preview
            cv2.imshow("Card Capture Preview", display_frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '):  # SPACE - Capture
                self.capture_image(frame)
            elif key == ord('q') or key == 27:  # Q or ESC - Quit
                print("\n👋 Exiting...")
                self.running = False
            elif key == ord('r'):  # R - Reset counter
                self.counter = 0
                print("🔄 Counter reset to 0")
            elif key == ord('h'):  # H - Toggle help
                show_help = not show_help
            elif key == ord('c'):  # C - Change camera
                print("\nEnter new camera index (0-5):")
                try:
                    new_index = int(input("Camera: "))
                    self.camera_index = new_index
                    if self.connect_camera():
                        print(f"✓ Switched to camera {new_index}")
                    else:
                        print(f"❌ Camera {new_index} not available")
                except ValueError:
                    print("❌ Invalid input")

        self.cleanup()
        return True

    def cleanup(self):
        """Clean up resources."""
        if self.capture:
            self.capture.release()
        cv2.destroyAllWindows()
        print(f"\n{'='*60}")
        print(f"Session Summary")
        print(f"{'='*60}")
        print(f"Total images captured: {self.counter}")
        print(f"Output folder: {self.raw_dir}")
        print(f"Metadata file: {self.metadata_file}")
        print(f"{'='*60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Yu-Gi-Oh Card Dataset Capture Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python capture_cards.py --camera 0
  python capture_cards.py --camera 0 --label blue_eyes_white_dragon
  python capture_cards.py --camera 0 --show-roi
  python capture_cards.py --camera 0 --roi 50 50 400 600

Keyboard Controls in Preview:
  SPACE       Capture image
  Q / ESC     Quit
  R           Reset counter
  C           Change camera index
  H           Toggle help overlay
        """
    )

    parser.add_argument("--camera", type=int, default=0,
                       help="Camera device index (default: 0)")
    parser.add_argument("--label", type=str, default="unknown",
                       help="Label prefix for filenames (default: unknown)")
    parser.add_argument("--output", type=str, default="data/captured_cards",
                       help="Output directory (default: data/captured_cards)")
    parser.add_argument("--width", type=int, default=1280,
                       help="Capture width in pixels (default: 1280)")
    parser.add_argument("--height", type=int, default=720,
                       help="Capture height in pixels (default: 720)")
    parser.add_argument("--show-roi", action="store_true",
                       help="Draw default ROI rectangle on preview")
    parser.add_argument("--roi", type=int, nargs=4, metavar=("X", "Y", "W", "H"),
                       help="ROI as: x y width height (saves cropped images)")

    args = parser.parse_args()

    # Parse ROI if provided
    roi = None
    if args.roi:
        roi = tuple(args.roi)

    # Create and run utility
    util = CardCaptureUtility(
        camera_index=args.camera,
        label=args.label,
        output_dir=args.output,
        width=args.width,
        height=args.height,
        roi=roi,
        show_roi=args.show_roi,
    )

    success = util.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
