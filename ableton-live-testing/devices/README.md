# Local Development UI for Arranger System

This directory contains UI options for local Live mode development.

## 1. Max for Live Device (`ArrangerControl.amxd`)

**What it is:**

- A Max for Live device that sits in your Live set
- Provides buttons and controls to send OSC messages to the arranger server
- Displays server replies

**Controls:**

- **Play** button → sends `/live/play`
- **Stop** button → sends `/live/stop`
- **Tempo** number box → sends `/live/set_tempo <value>`
- **New Scene** button → sends `/live/create_scene_index -1`
- **Server Reply** display → shows incoming OSC replies

**How to build (the .amxd file provided is JSON only; you must create it in Max):**

See `BUILD_GUIDE.md` in this folder for step-by-step Max patcher instructions with ASCII diagrams.

**How to use:**

1. Build the device in Max using the guide, then save as `.amxd`
2. Drag the saved device into a MIDI track in Live
3. Make sure the arranger OSC server is running:

   ```bash
   export PYTHONPATH="$PWD/python/src"
   ./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
   ```

4. Click buttons in the device to control Live via OSC
5. Watch the reply box for server responses

**Pros:**
- Lives in your Live set; always visible
- No browser or external app needed
- Direct visual feedback in device rack
- Can save with your Live project

**Cons:**
- Limited UI space
- Manual Max editing to add more controls

---

## 2. Web Dashboard (`web_dashboard.py`)

**What it is:**
- A Flask web server with a browser-based UI
- Full control panel with sliders, buttons, and state display
- Auto-refreshes Live state every 2 seconds

**Features:**
- Transport controls (Play/Stop with status indicator)
- Tempo slider (60-180 BPM)
- Scene creation and triggering
- MIDI clip creation (track/scene/length inputs)
- Track volume control
- Server reply monitor

**How to use:**
1. Install Flask (if not already):
   ```bash
   ./.venv/bin/pip install flask flask-cors
   ```

2. Start the arranger OSC server (in one terminal):
   ```bash
   export PYTHONPATH="$PWD/python/src"
   ./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
   ```

3. Start the web dashboard (in another terminal):
   ```bash
   export PYTHONPATH="$PWD/python/src"
   ./.venv/bin/python python/examples/web_dashboard.py
   ```

4. Open your browser to: `http://localhost:5000`

**Pros:**
- Rich UI with sliders, grids, status indicators
- Auto-refresh state polling
- Easy to extend (just edit HTML/JS)
- Works on any device on your network (phone/tablet)
- No Max for Live license needed

**Cons:**
- Requires browser open
- Extra Python process to run
- Network latency (minimal on localhost)

---

## Recommended Workflow

**For quick in-Live testing:**
- Use the Max for Live device
- Keep it visible in your device rack
- One-click play/stop/tempo/scene creation

**For detailed monitoring and control:**
- Use the web dashboard
- Keep browser on second monitor
- Full view of state and logs

**For production/performance:**
- Max for Live device for essential controls
- Web dashboard for tech/debug view
- Both can run simultaneously

---

## Next Steps

- **Extend Max device:** Add more buttons (trigger specific scenes, create clips with chord input)
- **Enhance dashboard:** Add scene list view, track meters, chord progression input
- **Mobile-friendly:** Make dashboard responsive for iPad/phone control
- **WebSocket upgrade:** Real-time push updates instead of polling

See `python/LIVE_INTEGRATION_GUIDE.md` for OSC endpoint reference.
