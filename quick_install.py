#!/usr/bin/env python
"""
Quick install script - Sets up backend and frontend with one command.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, description=""):
    """Run a shell command and report results."""
    if description:
        print(f"\n📦 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        print(f"   Error: {e}")
        return False


def main():
    project_root = Path(__file__).parent
    
    print("🎴 Yu-Gi-Oh Card Identifier - Quick Install")
    print("=" * 50)
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True)
        print(f"✓ Python: {result.stdout.decode().strip()}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node
    try:
        result = subprocess.run(["node", "--version"], capture_output=True)
        print(f"✓ Node: {result.stdout.decode().strip()}")
    except:
        print("❌ Node.js not found")
        return False
    
    # Backend setup
    print("\n" + "=" * 50)
    print("BACKEND SETUP")
    print("=" * 50)
    
    backend_dir = project_root / "backend"
    
    if sys.platform == "win32":
        # Windows
        venv_activate = backend_dir / "venv" / "Scripts" / "activate.bat"
        separator = "&"
    else:
        # Unix
        venv_activate = backend_dir / "venv" / "bin" / "activate"
        separator = ";"
    
    # Create venv
    if not (backend_dir / "venv").exists():
        if not run_command(
            f"{sys.executable} -m venv venv",
            cwd=backend_dir,
            description="Creating Python virtual environment"
        ):
            return False
    else:
        print("✓ Virtual environment already exists")
    
    # Install requirements
    if sys.platform == "win32":
        pip_cmd = str(backend_dir / "venv" / "Scripts" / "pip.exe")
    else:
        pip_cmd = f"source {venv_activate} && pip"
    
    if not run_command(
        f"{pip_cmd} install -r requirements.txt",
        cwd=backend_dir,
        description="Installing Python dependencies"
    ):
        return False
    
    # Frontend setup
    print("\n" + "=" * 50)
    print("FRONTEND SETUP")
    print("=" * 50)
    
    frontend_dir = project_root / "frontend"
    
    if not run_command(
        "npm install",
        cwd=frontend_dir,
        description="Installing npm dependencies"
    ):
        return False
    
    print("\n" + "=" * 50)
    print("✅ SETUP COMPLETE!")
    print("=" * 50)
    print("""
Next steps:

1. Open Terminal 1:
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

2. Open Terminal 2:
   cd frontend
   npm start

3. Browser opens at http://localhost:3000

For more details, see SETUP.md
""")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
