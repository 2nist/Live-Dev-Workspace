#!/bin/bash
# =============================================================================
# Devible - Professional Max for Live IDE
# Easy Launch Script for macOS/Linux
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ASCII Art Header
echo ""
echo -e "${PURPLE}"
echo "  ████████╗ ███████╗ ██╗   ██╗ ██╗ ██████╗  ██╗     ███████╗"
echo "  ██╔══██║ ██╔════╝ ██║   ██║ ██║ ██╔══██╗ ██║     ██╔════╝"
echo "  ██║  ██║ █████╗   ██║   ██║ ██║ ██████╔╝ ██║     █████╗"
echo "  ██║  ██║ ██╔══╝   ╚██╗ ██╔╝ ██║ ██╔══██╗ ██║     ██╔══╝"
echo "  ██████╔╝ ███████╗  ╚████╔╝  ██║ ██████╔╝ ███████╗███████╗"
echo "  ╚═════╝  ╚══════╝   ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝╚══════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}  Professional Max for Live IDE - v2.0 Beta${NC}"
echo -e "${BLUE}  The Future of Visual Music Programming${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js not found!${NC}"
    echo ""
    echo "Please install Node.js 18+ from: https://nodejs.org"
    echo ""
    echo "On macOS with Homebrew: brew install node"
    echo "On Ubuntu/Debian: sudo apt install nodejs npm"
    echo ""
    echo "After installation, restart this script."
    exit 1
fi

# Check Node.js version
echo -e "${BLUE}[INFO] Checking Node.js version...${NC}"
NODE_VERSION=$(node -v)
echo -e "${BLUE}[INFO] Node.js version: $NODE_VERSION${NC}"

# Navigate to project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/max-live-ide"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}[ERROR] package.json not found!${NC}"
    echo -e "${RED}[ERROR] Please ensure you're running this from the correct directory.${NC}"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo ""
    echo -e "${YELLOW}[INFO] Installing dependencies... This may take a few minutes.${NC}"
    echo -e "${YELLOW}[INFO] ⏳ Setting up Devible for first-time use...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install dependencies!${NC}"
        exit 1
    fi
    echo -e "${GREEN}[SUCCESS] ✅ Dependencies installed successfully!${NC}"
fi

# Start the development server
echo ""
echo -e "${GREEN}[INFO] 🚀 Starting Devible...${NC}"
echo -e "${GREEN}[INFO] Opening browser at http://localhost:3000${NC}"
echo ""
echo -e "${GREEN}[INFO] Ready to create amazing Max for Live devices!${NC}"
echo -e "${GREEN}[INFO] Press Ctrl+C to stop the server when done.${NC}"
echo ""

# Open browser after a short delay (macOS and Linux)
if command -v open &> /dev/null; then
    # macOS
    (sleep 3 && open "http://localhost:3000") &
elif command -v xdg-open &> /dev/null; then
    # Linux
    (sleep 3 && xdg-open "http://localhost:3000") &
fi

# Start the React development server
npm start

# If we get here, the server was stopped
echo ""
echo -e "${BLUE}[INFO] Devible server stopped.${NC}"
echo -e "${BLUE}[INFO] Thanks for using Devible! 🎵✨${NC}"
