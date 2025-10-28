# Arranger Control - Desktop App

Standalone Electron desktop application for controlling Ableton Live via the Arranger OSC server.

## Features

- **Transport Controls**: Play, Stop, and adjust tempo
- **Scene Management**: Create and trigger scenes
- **Clip Controls**: Create clips on specific tracks/scenes
- **Track Controls**: Volume, pan, mute, solo, and arm recording
- **Real-time Status**: Live connection indicator and tempo display
- **Auto-reconnect**: Automatically reconnects to OSC server when available

## Prerequisites

1. **Node.js** installed (v16 or higher)
2. **Arranger OSC server** running in the Live-Dev-Workspace
3. **Ableton Live** (for full functionality)

## Quick Start

### 1. Install Dependencies

```bash
cd arranger-control-app
npm install
```

### 2. Start the OSC Server

In a separate terminal, from the Live-Dev-Workspace root:

```bash
export PYTHONPATH="$PWD/python/src"
./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
```

### 3. Run the App

Development mode (with hot reload):

```bash
npm run dev
```

This will:
- Start the React dev server on port 3001
- Launch Electron window with DevTools
- Auto-reload on code changes

### 4. Build Standalone App

To create a distributable macOS .app:

```bash
npm run build
npm run package:mac
```

The packaged app will be in `dist/mac/`.

## Usage

1. Launch the app
2. Wait for "Connected" status (green badge in header)
3. Use controls to interact with Ableton Live:
   - **Play/Stop**: Control Live transport
   - **Tempo Slider**: Adjust BPM (60-180)
   - **Create Scene**: Add new scene at end
   - **Trigger Scene**: Launch scene by index
   - **Create Clip**: Add MIDI clip at track/scene position
   - **Track Controls**: Adjust volume, pan, mute/solo/arm

## Configuration

Default OSC server: `localhost:12000`

To change, edit `src/App.js`:

```javascript
const [client] = useState(() => new ArrangerOSCClient({
  host: 'localhost',  // Change this
  port: 12000,        // Or this
  onStatusChange: (connected) => setConnected(connected)
}));
```

## Troubleshooting

**"Disconnected" status:**
- Verify OSC server is running
- Check port 12000 is not in use by another process
- Ensure PYTHONPATH is set correctly

**Electron window doesn't open:**
- Wait for "webpack compiled" message before Electron launches
- Check console for React build errors

**Controls not responding:**
- Verify Ableton Live is running
- Check OSC server logs for errors
- Test with mock mode: `--use-mock` instead of `--use-live`

## Development

**File Structure:**
```
arranger-control-app/
├── electron/
│   └── main.js              # Electron main process
├── src/
│   ├── App.js               # Main React component
│   ├── index.js             # React entry point
│   ├── ArrangerOSC.js       # OSC client wrapper
│   └── components/
│       ├── TransportControls.js
│       ├── SceneControls.js
│       ├── ClipControls.js
│       └── TrackControls.js
├── public/
│   └── index.html
└── package.json
```

**Tech Stack:**
- Electron 28
- React 18
- Mantine UI 7
- Tabler Icons

## License

Part of the Live-Dev-Workspace project.
