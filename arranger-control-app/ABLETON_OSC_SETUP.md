# AbletonOSC Setup Guide

To use the Arranger Control app with Ableton Live, you need to install **AbletonOSC** - a MIDI Remote Script that exposes Live's API via OSC.

## Architecture

```
Electron App (arranger-control-app)
         ↓
Arranger OSC Server (port 12000)
         ↓
AbletonOSC Script (port 11000)
         ↓
Ableton Live API
```

## Step 1: Install AbletonOSC

### macOS Installation

1. **Locate the AbletonOSC folder** in this workspace:
   ```
   /Users/Matthew/Live_Dev/Live-Dev-Workspace/AbletonOSC-master
   ```

2. **Copy to Ableton's User Library**:
   ```bash
   # Navigate to your workspace
   cd /Users/Matthew/Live_Dev/Live-Dev-Workspace
   
   # Copy AbletonOSC to the correct location
   cp -r AbletonOSC-master ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonOSC
   ```

3. **Verify the copy**:
   ```bash
   ls -la ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonOSC
   ```
   
   You should see files like: `__init__.py`, `handler.py`, `osc_server.py`, etc.

## Step 2: Configure Ableton Live

1. **Restart Ableton Live** (if running)

2. **Open Preferences**:
   - macOS: `Live` → `Preferences` (or `⌘,`)

3. **Navigate to Link/Tempo/MIDI**:
   - Click the "Link Tempo MIDI" tab

4. **Select AbletonOSC**:
   - Under "Control Surface", select **AbletonOSC** from the dropdown
   - Input and Output should remain "None"

5. **Look for confirmation**:
   - Live should display: **"AbletonOSC: Listening for OSC on port 11000"**
   - Check the bottom of the Live window for this message

## Step 3: Start the Arranger OSC Server

Now start your Python OSC server that will communicate with AbletonOSC:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace

# Set Python path
export PYTHONPATH="$PWD/python/src"

# Start server with Live connection
./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
```

You should see:
```
Arranger OSC server running on ('127.0.0.1', 12000)
```

The `--use-live` flag tells it to connect to AbletonOSC on port 11000.

## Step 4: Launch the Electron App

In a **new terminal**:

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/arranger-control-app
npm run dev
```

The app should:
- Open at 1200x800
- Show "Connected" (green badge) in the header
- Display current tempo from Live

## Troubleshooting

### "Disconnected" Status in App

**Cause**: Arranger OSC server not running or not reachable

**Fix**:
```bash
# Check if server is running
lsof -i :12000

# If nothing, start it:
export PYTHONPATH="/Users/Matthew/Live_Dev/Live-Dev-Workspace/python/src"
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace
./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
```

### "AbletonOSC not found" in Live Preferences

**Cause**: Folder not in correct location or named incorrectly

**Fix**:
```bash
# Check the folder exists and is named correctly
ls ~/Music/Ableton/User\ Library/Remote\ Scripts/

# Should show "AbletonOSC" folder
# If not, copy again:
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace
cp -r AbletonOSC-master ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonOSC
```

Then restart Ableton Live.

### "No valid input/output ports"

**Cause**: This error means AbletonOSC isn't loaded in Live yet

**Fix**:
1. Verify AbletonOSC folder is in `~/Music/Ableton/User Library/Remote Scripts/`
2. Restart Ableton Live completely
3. Go to Preferences → Link/Tempo/MIDI
4. Select "AbletonOSC" from Control Surface dropdown
5. Look for "Listening for OSC on port 11000" message

### OSC Server Errors

**Cause**: Python dependencies or path issues

**Fix**:
```bash
# Ensure venv is activated and deps installed
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python
../.venv/bin/pip install pythonosc

# Try running with explicit path
export PYTHONPATH="/Users/Matthew/Live_Dev/Live-Dev-Workspace/python/src"
../.venv/bin/python src/arranger/live_bridge/osc_server.py --use-live
```

### Test AbletonOSC Directly

You can test if AbletonOSC is working without the Arranger server:

```bash
# Install pythonosc in venv if needed
.venv/bin/pip install pythonosc

# Create a quick test script
cat > test_abletonosc.py << 'EOF'
from pythonosc import udp_client
import time

client = udp_client.SimpleUDPClient("127.0.0.1", 11000)

print("Sending test message to AbletonOSC...")
client.send_message("/live/test", [])

time.sleep(1)
print("If AbletonOSC is working, you should see a message in Live!")
EOF

# Run it
.venv/bin/python test_abletonosc.py
```

If working, you'll see "AbletonOSC: received /live/test" in Live.

## Mock Mode (Development Without Live)

To develop without Ableton Live running:

```bash
# Start server in mock mode (omit --use-live)
export PYTHONPATH="$PWD/python/src"
./.venv/bin/python python/src/arranger/live_bridge/osc_server.py
```

Mock mode simulates Live responses for testing UI/UX.

## Port Configuration

| Service               | Port  | Purpose                          |
|-----------------------|-------|----------------------------------|
| AbletonOSC (receive)  | 11000 | Receives OSC commands            |
| AbletonOSC (reply)    | 11001 | Sends OSC replies                |
| Arranger OSC (receive)| 12000 | Your app sends commands here     |
| Arranger OSC (reply)  | 12001 | Arranger sends replies here      |
| React Dev Server      | 3001  | Electron loads UI from here      |

## Quick Start Commands

**Terminal 1** (Arranger OSC Server):
```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace
export PYTHONPATH="$PWD/python/src"
./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
```

**Terminal 2** (Electron App):
```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/arranger-control-app
npm run dev
```

**Ableton Live**:
- AbletonOSC selected in Preferences → Link/Tempo/MIDI → Control Surface
- Message visible: "AbletonOSC: Listening for OSC on port 11000"

## Next Steps

Once connected:
1. **Play/Stop**: Control Live transport
2. **Tempo**: Adjust BPM (changes reflected in Live)
3. **Scenes**: Create and trigger scenes
4. **Clips**: Create MIDI clips
5. **Tracks**: Control volume, pan, mute, solo, arm

All changes appear immediately in Ableton Live!
