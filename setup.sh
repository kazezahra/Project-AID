#!/bin/bash

# Autism Pre-Screening Tool - Quick Start Script
# This script sets up and runs the entire application

set -e

echo "🧠 Autism Pre-Screening Tool - Quick Start"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo -e "${RED}Error: pip is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip found${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r app/api/requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=1
GROQ_API_KEY=your_api_key_here
EOF
    echo -e "${GREEN}✓ .env file created (update GROQ_API_KEY)${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To start the application:"
echo "1. Update .env file with your API keys"
echo "2. Run: python -m flask --app app.api.app run --host 0.0.0.0 --port 5000"
echo "3. Open http://localhost:8000 in your browser"
echo ""
echo "To serve the frontend:"
echo "   cd frontend/AID-FYP"
echo "   python -m http.server 8000"
echo ""
echo "Or use Docker:"
echo "   docker-compose up"
echo ""
