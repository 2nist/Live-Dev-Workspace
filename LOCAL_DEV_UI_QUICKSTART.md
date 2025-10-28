# Quick Start: Local Live Mode UI

Both UIs are now ready. Pick your workflow:

## Option A: Max for Live Device (in-Live controls)

1. **Start the OSC server** (terminal 1):
   ```bash
   cd /Users/Matthew/Live_Dev/Live-Dev-Workspace
   export PYTHONPATH="$PWD/python/src"
   ./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
   ```

2. **Open Live and load the device:**
   - Drag `ableton-live-testing/devices/ArrangerControl.amxd` into any MIDI track
   - Click buttons to control Live via OSC

## Option B: Web Dashboard (browser-based monitoring)

1. **Start the OSC server** (terminal 1):
   ```bash
   cd /Users/Matthew/Live_Dev/Live-Dev-Workspace
   export PYTHONPATH="$PWD/python/src"
   ./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
   ```

2. **Start the web dashboard** (terminal 2):
   ```bash
   cd /Users/Matthew/Live_Dev/Live-Dev-Workspace
   export PYTHONPATH="$PWD/python/src"
   ./.venv/bin/python python/examples/web_dashboard.py
   ```

3. **Open browser:**
   - Navigate to: `http://localhost:5000`
   - Control Live from the dashboard

## Option C: Both (recommended)

Run both simultaneously:
- Max device for quick in-Live controls
- Web dashboard on second monitor for detailed state/debugging

See `ableton-live-testing/devices/README.md` for detailed feature comparison.
