# Arranger OSC Quick Reference

## Starting the Server

```python
from arranger.live_bridge.osc_server import ArrangerOSCServer

server = ArrangerOSCServer(ip="127.0.0.1", port=12000, reply_port=12001)
server.serve_forever()
```

## OSC Message Endpoints

### Theory Guidance

| Endpoint | Args | Description |
|----------|------|-------------|
| `/theory/guidance` | key, mode, chord | Get theory suggestions for context |
| `/theory/progressions` | key, mode | Get common chord progressions |
| `/theory/cadences` | - | Get all cadence types |
| `/theory/analyze_arrangement` | JSON string | Analyze arrangement structure |

### Live Integration

| Endpoint | Args | Description |
|----------|------|-------------|
| `/live/theory_suggestions` | JSON string | Get real-time theory suggestions |
| `/live/create_scene` | name, *clips | Create a scene in Live |
| `/live/create_chord_clip` | chord, length, track | Create MIDI clip |
| `/live/schedule_playback` | *order | Schedule section playback |

## Client Examples

### Python OSC Client

```python
from pythonosc import udp_client
import json

client = udp_client.SimpleUDPClient("127.0.0.1", 12000)

# Theory guidance
client.send_message("/theory/guidance", ["C", "major", "I"])

# Progressions
client.send_message("/theory/progressions", ["C", "major"])

# Create scene
client.send_message("/live/create_scene", ["Verse1", "drums", "bass", "keys"])

# Create chord clip
client.send_message("/live/create_chord_clip", ["Cmaj7", 4, 1])

# Schedule playback
client.send_message("/live/schedule_playback", ["Intro", "V1", "C", "V2", "C"])

# Analyze arrangement (send as JSON string)
arrangement = json.dumps({
    "key": "C",
    "mode": "major",
    "sections": [
        {"label": "V", "type": "verse", "bars": 8},
        {"label": "C", "type": "chorus", "bars": 8}
    ]
})
client.send_message("/theory/analyze_arrangement", [arrangement])
```

### Max/MSP OSC Client

```max
[udpsend 127.0.0.1 12000]
|
[prepend send]
|
[/theory/guidance C major I(
```

## Live Bridge Direct Usage

```python
from arranger.live_bridge.live_bridge import (
    SceneManager, ChordClipFactory, PlaybackScheduler
)

# Scene management
scene_mgr = SceneManager()
scene_idx = scene_mgr.create_scene("Chorus", [
    {"track": 1, "clip": "drums"},
    {"track": 2, "clip": "bass"}
])
scenes = scene_mgr.list_scenes()

# Chord clip creation
clip_factory = ChordClipFactory()
clip_data = clip_factory.create_chord_clip("Dm7", 4, 2)
# Returns: {"track": 2, "notes": [38, 41, 45, 48], "length": 4}

# Playback scheduling
scheduler = PlaybackScheduler()
scheduler.schedule_playback(["Intro", "Verse", "Chorus"])
order = scheduler.get_current_order()
```

## Music Theory API

```python
from arranger.utils.music_theory import (
    get_common_progressions,
    get_cadence,
    get_borrowed_chords,
    get_substitutions,
    get_theory_guidance,
    add_progression,  # User extension
    add_cadence,      # User extension
)

# Get progressions
progressions = get_common_progressions("C", "major")
# Returns: [["I", "IV", "V"], ["ii", "V", "I"], ...]

# Get cadence
cadence = get_cadence("authentic")
# Returns: ["V", "I"]

# Get borrowed chords
borrowed = get_borrowed_chords("C", "major")
# Returns: ["bIII", "bVI", "bVII"]

# Get substitutions
subs = get_substitutions("V7", "tritone")
# Returns: ["bII7"]

# Get all guidance
guidance = get_theory_guidance({
    "key": "C",
    "mode": "major",
    "chord": "V7"
})
# Returns comprehensive theory guidance dict

# Add custom progression
add_progression("major", ["I", "iii", "vi", "IV"])

# Add custom cadence
add_cadence("modal", ["bVII", "I"])
```

## Testing

```bash
# Run all tests
pytest python/tests/test_arranger/ -v

# Run unit tests only
pytest python/tests/test_arranger/unit/ -v

# Run integration tests only
pytest python/tests/test_arranger/integration/ -v

# Run with coverage
pytest python/tests/test_arranger/ --cov=arranger --cov-report=html
```

## Port Configuration

- **OSC Server Receive**: 12000
- **OSC Server Reply**: 12001
- **AbletonOSC**: 11000 (default)

## JSON Data Format

When sending complex data (dicts) via OSC, serialize to JSON string:

```python
import json

# Arrangement data
data = {
    "key": "C",
    "mode": "major",
    "sections": [...]
}

# Send as JSON string
client.send_message("/theory/analyze_arrangement", [json.dumps(data)])
```

Server handlers automatically parse JSON strings back to dicts.
