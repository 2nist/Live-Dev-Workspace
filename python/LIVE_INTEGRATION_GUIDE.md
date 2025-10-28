# Ableton Live Integration Guide

## Overview

The arranger system now includes full integration with Ableton Live via the AbletonOSC remote script. This enables:

- Creating and managing scenes programmatically
- Generating MIDI clips from chord progressions
- Scheduling and triggering playback
- Querying and controlling Live's transport
- Building complete song arrangements in Live

## Prerequisites

1. **Ableton Live 11+** installed and running
2. **AbletonOSC** remote script installed (included in this repository)
3. **Python environment** with arranger package

## Installing AbletonOSC

1. Locate the AbletonOSC folder:
   ```
   /Users/Matthew/Live_Dev/Live-Dev-Workspace/AbletonOSC-master
   ```

2. Copy to your Live User Library:
   - **macOS**: `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows**: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\`

3. Restart Ableton Live

4. In Live Preferences → Link/Tempo/MIDI:
   - Set "Control Surface" to "AbletonOSC"
   - You should see: "AbletonOSC: Listening for OSC on port 11000"

## Connection Modes

### Mock Mode (Default)
- Works without Live connection
- Returns simulated data
- Used for testing and development

### Live Mode
- Requires running Ableton Live with AbletonOSC
- Full bi-directional control
- Real-time feedback

## Basic Usage

### Connecting to Live

```python
from arranger.live_bridge.ableton_connection import AbletonConnection

# Auto-detect Live (falls back to mock if not available)
ableton = AbletonConnection(mock=False)

# Explicit connection
ableton = AbletonConnection(
    hostname="127.0.0.1",
    port=11000,
    client_port=11001,
    mock=False
)

# Check connection status
if ableton.is_connected():
    print("Connected to Live!")
else:
    print("Running in mock mode")
```

### Creating Scenes

```python
from arranger.live_bridge.live_bridge import SceneManager

scene_mgr = SceneManager(ableton)

# Create a scene
scene_idx = scene_mgr.create_scene("Verse", [])
print(f"Created scene at index {scene_idx}")

# List all scenes
scenes = scene_mgr.list_scenes()
print(f"Scenes: {scenes}")

# Trigger a scene
scene_mgr.trigger_scene(scene_idx)
```

### Creating Chord Clips

```python
from arranger.live_bridge.live_bridge import ChordClipFactory

clip_factory = ChordClipFactory(ableton)

# Create a chord clip on track 0, length 4 bars
result = clip_factory.create_chord_clip("Cmaj7", length=4, track=0)

print(f"Created clip with notes: {result['notes']}")
print(f"Connected to Live: {result['connected']}")
```

### Building an Arrangement

```python
# Create scenes with chord progressions
scenes = [
    ("Intro", ["C", "Am", "F", "G"]),
    ("Verse", ["C", "G", "Am", "F"]),
    ("Chorus", ["F", "G", "C", "Am"]),
    ("Bridge", ["Dm", "Em", "F", "G"])
]

for scene_name, chords in scenes:
    scene_idx = scene_mgr.create_scene(scene_name, [])
    
    for track_idx, chord in enumerate(chords):
        clip_factory.create_chord_clip(chord, 4, track_idx)
```

### Scheduling Playback

```python
from arranger.live_bridge.live_bridge import PlaybackScheduler

scheduler = PlaybackScheduler(ableton)

# Define playback order
order = [
    "Intro",
    "Verse", "Chorus",
    "Verse", "Chorus",
    "Bridge",
    "Chorus"
]

# Schedule the arrangement
result = scheduler.schedule_playback(order)
print(f"Scheduled: {result['order']}")

# Trigger scenes in sequence
while scheduler.get_current_order():
    next_scene = scheduler.trigger_next()
    print(f"Playing: {next_scene}")
    time.sleep(16)  # Wait for scene to finish (4 bars at 120 BPM)
```

### Transport Control

```python
# Get/set tempo
tempo = ableton.get_tempo()
print(f"Current tempo: {tempo} BPM")

ableton.set_tempo(128.0)

# Get time signature
time_sig = ableton.get_time_signature()
print(f"Time signature: {time_sig[0]}/{time_sig[1]}")

# Transport controls
ableton.play()   # Start playback
ableton.stop()   # Stop playback
```

### Querying Live State

```python
# Get number of tracks and scenes
num_tracks = ableton.get_num_tracks()
num_scenes = ableton.get_num_scenes()

print(f"Tracks: {num_tracks}, Scenes: {num_scenes}")

# Get track names
for i in range(num_tracks):
    name = ableton.get_track_name(i)
    print(f"Track {i}: {name}")

# Get scene names
scene_names = ableton.get_scene_names()
for i, name in enumerate(scene_names):
    print(f"Scene {i}: {name}")
```

## Complete Example

See `python/examples/live_integration_example.py` for a complete working example that:

1. Connects to Ableton Live
2. Creates a multi-section arrangement (Intro, Verse, Chorus, Bridge)
3. Generates chord clips for each section
4. Schedules playback order
5. Demonstrates transport control

Run it with:
```bash
cd python
python examples/live_integration_example.py
```

## OSC Server Integration

The arranger OSC server can be configured to use Live integration:

```python
from arranger.live_bridge.osc_server import ArrangerOSCServer

# Start server with Live integration
server = ArrangerOSCServer(
    ip="127.0.0.1",
    port=12000,
    reply_port=12001,
    ableton_host="127.0.0.1",
    ableton_port=11000,
    use_live=True  # Enable Live integration
)

server.serve_forever()
```

### Run the OSC server from CLI

Recommended (macOS):

```bash
# From repo root
export PYTHONPATH="$PWD/python/src"
./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --ip 127.0.0.1 --port 12000 --reply 12001 --use-live
```

Mock mode (no Live required):

```bash
export PYTHONPATH="$PWD/python/src"
./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --ip 127.0.0.1 --port 12000 --reply 12001
```

Quick demo client (sends a few messages):

```bash
export PYTHONPATH="$PWD/python/src"
./.venv/bin/python python/examples/osc_client_demo.py
```

Now OSC messages will create actual scenes and clips in Live:

```python
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 12000)

# Create scene in Live
client.send_message("/live/create_scene", ["Verse1", "drums", "bass"])

# Create chord clip in Live
client.send_message("/live/create_chord_clip", ["Cmaj7", 4, 0])
```

### Endpoints Quick Reference

- Transport
    - `/live/play`
    - `/live/stop`
    - `/live/set_tempo <float>`
    - `/live/get_tempo`
    - `/live/get_time_signature`
- Scenes
    - `/live/create_scene <name> [clipNames...]`
    - `/live/create_scene_index <index>` (use `-1` to append)
    - `/live/trigger_scene <index>`
- Clips
    - `/live/clip/create <track:int> <scene:int> <length:float>`
    - `/live/clip/add_note <track:int> <scene:int> <pitch:int> <start:float> <dur:float> <vel:int>`
- Tracks
    - `/live/track/set/volume <track:int> <volume:0..1>`
    - `/live/track/get/volume <track:int>`
    - `/live/track/set/pan <track:int> <pan:-1..1>`
    - `/live/track/set/mute <track:int> <0|1>`
    - `/live/track/set/solo <track:int> <0|1>`
    - `/live/track/set/arm <track:int> <0|1>`

## AbletonConnection API Reference

### Connection Methods
- `is_connected()` - Check if connected to Live
- `close()` - Close the connection

### Transport Methods
- `get_tempo()` - Get current tempo
- `set_tempo(tempo)` - Set tempo
- `get_time_signature()` - Get time signature as (numerator, denominator)
- `play()` - Start playback
- `stop()` - Stop playback

### Scene Methods
- `get_num_scenes()` - Get number of scenes
- `get_scene_names()` - Get list of all scene names
- `create_scene(index=-1)` - Create scene at index (-1 = end)
- `set_scene_name(scene_index, name)` - Set scene name
- `trigger_scene(scene_index)` - Fire a scene

### Track Methods
- `get_num_tracks()` - Get number of tracks
- `get_track_name(track_index)` - Get track name

### Clip Methods
- `create_midi_clip(track, scene, length)` - Create MIDI clip
- `add_midi_notes(track, scene, notes)` - Add MIDI notes to clip
  - `notes`: List of `(pitch, start_time, duration, velocity)` tuples
- `set_clip_name(track, scene, name)` - Set clip name
- `trigger_clip(track, scene)` - Fire a clip

## Architecture

```
┌─────────────────────┐
│  Arranger System    │
│  (OSC Server,       │
│   Models, API)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Live Bridge       │
│  ┌───────────────┐  │
│  │ SceneManager  │  │
│  │ ChordClipFact │  │
│  │ Playback      │  │
│  │ Scheduler     │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │
           ▼
┌─────────────────────┐
│ AbletonConnection   │
│  (Wrapper for       │
│   AbletonOSC)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AbletonOSC Client  │
│  (pythonosc)        │
└──────────┬──────────┘
           │
           ▼
    [OSC Messages]
           │
           ▼
┌─────────────────────┐
│   Ableton Live      │
│   + AbletonOSC      │
│   Remote Script     │
└─────────────────────┘
```

## Troubleshooting

### Connection fails
1. Ensure Ableton Live is running
2. Check AbletonOSC is selected in Live Preferences
3. Verify port 11000 is not blocked
4. Check Live shows "AbletonOSC: Listening on port 11000"

### Clips not created
1. Ensure you have MIDI tracks in your Live set
2. Check track index is valid (0-based)
3. Verify sufficient empty clip slots
4. Check console for error messages

### Mock mode always active
1. Pass `mock=False` to AbletonConnection
2. Ensure Live is running with AbletonOSC
3. Check connection logs for errors

### Scenes not triggering
1. Verify scene exists (check `get_scene_names()`)
2. Ensure scene has clips
3. Check Live transport is not recording

## Testing

Run the Python tests (uses unittest):
```bash
./.venv/bin/python -m unittest discover -s python/tests -p 'test_*.py' -v
```

Included tests:
- Mock-mode Live bridge integration (transport, scenes, clips, scheduler)
- OSC server smoke test (binds and accepts theory messages)

## Next Steps

- Add device parameter control
- Implement clip looping and automation
- Add track volume/pan/mute/solo control
- Support for audio clips
- MIDI effects integration
- Live Set template generation
