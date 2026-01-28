# Max for Live Integration Guide

This guide explains how to integrate the Ableton Arranger system with Max for Live devices.

## Overview

The Arranger system exposes functionality via OSC (Open Sound Control), making it accessible from Max for Live devices. The OSC server runs on `127.0.0.1:12000` by default.

## OSC Server Setup

1. Start the OSC server:
```bash
python -m arranger.live_bridge.osc_server
```

2. Configure ports (defaults):
   - Server port: 12000 (receives messages)
   - Reply port: 12001 (sends responses)
   - AbletonOSC port: 11000

## Max for Live Integration

### Basic Setup in Max

1. Add an `udpsend` object to send OSC messages:
   ```
   udpsend 127.0.0.1 12000
   ```

2. Add an `udpreceive` object to receive responses:
   ```
   udpreceive 12001
   ```

### Common OSC Messages

#### Theory Endpoints

**Get Progressions**
```
/theory/progressions C major
```
Returns: List of common progressions for C major

**Get Cadences**
```
/theory/cadences
```
Returns: Dictionary of cadence types (authentic, plagal, deceptive, half)

**Get Theory Guidance**
```
/theory/guidance C major Cmaj7
```
Returns: Comprehensive theory guidance including substitutions, borrowed chords, etc.

#### Live Control Endpoints

**Play/Stop**
```
/live/play
/live/stop
```

**Create Chord Clip**
```
/live/create_chord_clip Cmaj7 4.0 0
```
Args: chord_name, length_in_beats, track_index

**Trigger Scene**
```
/live/trigger_scene 0
```
Args: scene_index

## Example Max for Live Patches

### Chord Progression Device

```
[udpsend 127.0.0.1 12000]
|
[prepend /theory/progressions]
|
[message C major]
|
[udpreceive 12001]
```

### Theory Guide Device

```
[udpsend 127.0.0.1 12000]
|
[prepend /theory/guidance]
|
[message C major Cmaj7]
|
[udpreceive 12001]
```

## Python API for Max for Live

You can also use the Python API directly in Max for Live's `py` object:

```python
import sys
sys.path.insert(0, '/path/to/arranger')

from arranger.api.m4l_bridge import M4LBridge

bridge = M4LBridge()
chords = bridge.get_chord_suggestions("C", "major")
midi_notes = bridge.create_chord_midi("Cmaj7", octave=4)
```

## Complete OSC Reference

See `arranger/api/m4l_bridge.py` for the complete OSC message reference dictionary.

## Troubleshooting

1. **Connection Issues**: Ensure the OSC server is running and ports are not blocked
2. **No Response**: Check that reply port (12001) is accessible
3. **Invalid Messages**: Verify message format matches OSC reference

## Advanced Usage

For advanced integration, see:
- `arranger/live_bridge/osc_server.py` - Full OSC server implementation
- `arranger/services/theory_service.py` - Theory service API
- `arranger/services/arrangement_service.py` - Arrangement building API
