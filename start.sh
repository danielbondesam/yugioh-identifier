#!/bin/bash

# Yu-Gi-Oh Identifier - Combined Start Script

set -e

echo "🎴 Yu-Gi-Oh Card Identifier - Starting..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running on Windows (Git Bash or WSL)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    BACKEND_CMD="cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    FRONTEND_CMD="cd frontend && npm start"
else
    BACKEND_CMD="cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    FRONTEND_CMD="cd frontend && npm start"
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        ss -tulpn | grep :$port >/dev/null 2>&1
    elif [[ "$OSTYPE" == "msys" ]]; then
        # Windows Git Bash
        netstat -ano | grep :$port >/dev/null 2>&1
    fi
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

echo -e "${GREEN}✓ Python and Node.js found${NC}"
echo ""

# Start backend
echo -e "${BLUE}Starting Backend (port 8000)...${NC}"
if check_port 8000; then
    echo -e "${GREEN}Port 8000 already in use${NC}"
else
    echo "Backend command: $BACKEND_CMD"
fi
echo ""

# Start frontend
echo -e "${BLUE}Starting Frontend (port 3000)...${NC}"
echo "Frontend command: $FRONTEND_CMD"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Open two terminal windows and run:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Then open: http://localhost:3000"
echo ""
