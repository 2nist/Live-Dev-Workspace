#!/bin/bash

echo "=========================================="
echo "AbletonOSC Installation Script"
echo "=========================================="
echo ""

# Paths
WORKSPACE_DIR="/Users/Matthew/Live_Dev/Live-Dev-Workspace"
SOURCE_DIR="$WORKSPACE_DIR/AbletonOSC-master"
DEST_DIR="$HOME/Music/Ableton/User Library/Remote Scripts/AbletonOSC"

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: AbletonOSC-master folder not found in workspace"
    echo "Expected: $SOURCE_DIR"
    exit 1
fi

echo "✅ Found AbletonOSC source folder"

# Create Remote Scripts directory if it doesn't exist
REMOTE_SCRIPTS_DIR="$HOME/Music/Ableton/User Library/Remote Scripts"
if [ ! -d "$REMOTE_SCRIPTS_DIR" ]; then
    echo "📁 Creating Remote Scripts directory..."
    mkdir -p "$REMOTE_SCRIPTS_DIR"
fi

# Remove old installation if exists
if [ -d "$DEST_DIR" ]; then
    echo "🗑️  Removing old AbletonOSC installation..."
    rm -rf "$DEST_DIR"
fi

# Copy AbletonOSC
echo "📦 Installing AbletonOSC..."
cp -r "$SOURCE_DIR" "$DEST_DIR"

# Verify installation
if [ -f "$DEST_DIR/__init__.py" ]; then
    echo ""
    echo "=========================================="
    echo "✅ AbletonOSC installed successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Restart Ableton Live (if running)"
    echo ""
    echo "2. In Live, go to:"
    echo "   Preferences → Link/Tempo/MIDI"
    echo ""
    echo "3. Under 'Control Surface', select:"
    echo "   AbletonOSC"
    echo ""
    echo "4. Look for confirmation message:"
    echo "   'AbletonOSC: Listening for OSC on port 11000'"
    echo ""
    echo "5. Start the Arranger OSC server:"
    echo "   cd $WORKSPACE_DIR"
    echo "   export PYTHONPATH=\"\$PWD/python/src\""
    echo "   ./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live"
    echo ""
    echo "6. Launch the control app:"
    echo "   cd arranger-control-app"
    echo "   npm run dev"
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    echo "Check that the source folder contains AbletonOSC files."
    exit 1
fi
