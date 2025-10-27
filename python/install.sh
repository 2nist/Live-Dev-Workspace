#!/bin/bash
# Installation script for live-dev-integration

set -e

echo "=== Live Dev Integration Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: Please run this script from the python/ directory"
    exit 1
fi

# Create virtual environment (optional)
read -p "Create virtual environment? (recommended) [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install package in development mode
echo "Installing live-dev-integration..."
pip install -e .

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Make sure AbletonOSC is installed in Ableton Live"
echo "  2. Start Ableton Live and enable AbletonOSC in Preferences"
echo "  3. Try running an example:"
echo "     cd examples"
echo "     python 01_basic_connection.py"
echo ""

# Offer to run test
read -p "Test connection now? (requires Live to be running) [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing connection..."
    python3 -c "
from live_dev import LiveConnection
try:
    with LiveConnection() as live:
        live.test_connection()
        print('✓ Connection test passed!')
except Exception as e:
    print(f'✗ Connection test failed: {e}')
    print('Make sure Ableton Live is running with AbletonOSC enabled')
"
fi

echo ""
echo "Setup complete! 🎵"
