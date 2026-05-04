#!/usr/bin/env python
"""
Project structure and file overview.
Run to visualize the complete project layout.
"""

import os
from pathlib import Path


def print_tree(directory, prefix="", max_depth=4, current_depth=0, ignore_dirs=None):
    """Print directory tree structure."""
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.env', 'venv', '.vscode'}
    
    if current_depth >= max_depth:
        return
    
    try:
        items = sorted(os.listdir(directory))
    except PermissionError:
        return
    
    # Filter ignored directories
    items = [i for i in items if i not in ignore_dirs]
    
    for i, item in enumerate(items):
        path = os.path.join(directory, item)
        is_last = i == len(items) - 1
        
        current_prefix = "└── " if is_last else "├── "
        print(prefix + current_prefix + item)
        
        if os.path.isdir(path) and item not in ignore_dirs:
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(path, next_prefix, max_depth, current_depth + 1, ignore_dirs)


def main():
    project_root = Path(__file__).parent
    
    print("\n")
    print("=" * 70)
    print("🎴 YU-GI-OH CARD IDENTIFIER - Project Structure".center(70))
    print("=" * 70)
    print()
    
    print("Project Root:", project_root)
    print()
    print("Directory Tree:")
    print()
    print_tree(str(project_root))
    
    print()
    print("=" * 70)
    print("Key Files Overview".center(70))
    print("=" * 70)
    print()
    
    files_info = {
        "README.md": "Project overview, features, tech stack, installation",
        "CLAUDE.md": "Internal architecture, design decisions, trade-offs",
        "SETUP.md": "Complete setup guide with troubleshooting",
        "API_TESTING.md": "API testing examples and debugging guide",
        "DOCKER.md": "Docker deployment and containerization",
        ".gitignore": "Git ignore patterns for Python and Node",
        "quick_install.py": "One-command installation script",
        
        "backend/": "Python FastAPI backend",
        "backend/app/main.py": "FastAPI app with all endpoints",
        "backend/app/config.py": "Configuration and constants",
        "backend/app/image_processor.py": "Image preprocessing for OCR",
        "backend/app/ocr_engine.py": "Tesseract OCR wrapper",
        "backend/app/card_matcher.py": "Fuzzy string matching logic",
        "backend/app/card_cache.py": "YGOPRODeck API and caching",
        "backend/app/dev_tools.py": "Development utilities",
        "backend/requirements.txt": "Python dependencies",
        "backend/Dockerfile": "Docker image for backend",
        "backend/.env.example": "Environment variables template",
        
        "frontend/": "React frontend application",
        "frontend/src/App.js": "Main React component",
        "frontend/src/components/CameraCapture.js": "Camera UI component",
        "frontend/src/components/ResultDisplay.js": "Results view component",
        "frontend/src/components/Header.js": "App header with status",
        "frontend/src/index.css": "Tailwind CSS styles",
        "frontend/package.json": "Node dependencies",
        "frontend/Dockerfile": "Docker image for frontend",
        "frontend/.env.example": "Environment variables template",
        "frontend/tailwind.config.js": "Tailwind configuration",
        
        "docker-compose.yml": "Docker Compose configuration",
    }
    
    for file_path, description in files_info.items():
        print(f"📄 {file_path:<40} {description}")
    
    print()
    print("=" * 70)
    print("Getting Started".center(70))
    print("=" * 70)
    print("""
1. Read SETUP.md for complete installation instructions

2. Quick start:
   - Backend: python -m uvicorn app.main:app --reload
   - Frontend: npm start
   - Visit http://localhost:3000

3. Test the API:
   - Documentation: http://localhost:8000/docs
   - Examples: See API_TESTING.md

4. Understand architecture:
   - Read CLAUDE.md for internal design
   - Review backend/app/main.py for API endpoints
   - Check frontend/src/App.js for React structure

5. Deploy with Docker:
   - See DOCKER.md for containerization
   - Run: docker-compose up

""")
    
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
