# Live Dev Integration

**Unified Python toolkit for Ableton Live and Max for Live device development**

This package integrates [pylive](https://github.com/ideoforms/pylive) and [AbletonOSC](https://github.com/ideoforms/AbletonOSC) to provide a comprehensive, easy-to-use Python interface for controlling Ableton Live and developing Max for Live devices.

## 🎯 Features

- **Unified API**: Single interface combining pylive's high-level API with AbletonOSC's comprehensive control
- **M4L Device Helpers**: Specialized utilities for Max for Live device development
- **Real-time OSC**: Listen and react to Live events in real-time
- **MIDI Generation**: Create and manipulate MIDI clips programmatically
- **Device Control**: Query and modify device parameters
- **Musical Utilities**: Scales, quantization, note conversion, and more

## 📋 Prerequisites

- **Ableton Live 11+**
- **Python 3.8+**
- **AbletonOSC** installed as a Control Surface in Live

### Installing AbletonOSC

1. Download [AbletonOSC](https://github.com/ideoforms/AbletonOSC/archive/refs/heads/master.zip)
2. Unzip and rename folder to `AbletonOSC`
3. Copy to your Remote Scripts folder:
   - **macOS**: `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows**: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\`
4. Restart Ableton Live
5. In Live: Preferences > Link / Tempo / MIDI > Control Surface > Select "AbletonOSC"

## 🚀 Quick Start

### Installation

```bash
# Navigate to the python directory
cd python

# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

### Basic Usage

```python
from live_dev import LiveConnection

# Connect to Live
with LiveConnection(scan_on_init=True) as live:
    # Query tempo
    print(f"Current tempo: {live.get_tempo()} BPM")
    
    # List tracks
    for i, track in enumerate(live.get_tracks()):
        print(f"Track {i}: {track.name}")
    
    # Start playback
    live.play()
    
    # Fire a clip
    live.fire_clip(track_index=0, clip_index=0)
```

### Max for Live Device Development

```python
from live_dev import LiveConnection, M4LDeviceHelper, create_scale

# Create helper with connection
helper = M4LDeviceHelper()

# Create a MIDI clip with a melody
root = 60  # C4
scale = create_scale(root, "minor")
melody = [scale[i % len(scale)] for i in range(16)]

helper.create_note_sequence(
    track_index=0,
    clip_index=0,
    pitches=melody,
    duration=0.25  # 16th notes
)

# Randomize device parameters (for generative effects)
helper.randomize_device_parameters(
    track_index=0,
    device_index=0,
    exclude_params=["Device On"]
)
```

## 📚 Examples

The `examples/` directory contains comprehensive examples:

| Example | Description | Level |
|---------|-------------|-------|
| `01_basic_connection.py` | Connect and query Live | Beginner |
| `02_clip_control.py` | Control clip playback | Beginner |
| `03_midi_generation.py` | Generate MIDI clips | Intermediate |
| `04_device_control.py` | Control device parameters | Intermediate |
| `05_osc_listeners.py` | Real-time event listening | Advanced |
| `06_m4l_template.py` | M4L device templates | Advanced |

Run examples with:
```bash
cd examples
python 01_basic_connection.py
```

## 🏗️ Architecture

```
python/
├── src/live_dev/              # Main package
│   ├── __init__.py            # Package exports
│   ├── live_connection.py     # Core connection manager
│   ├── m4l_helpers.py         # M4L device utilities
│   └── utils.py               # Helper functions
├── examples/                   # Example scripts
├── tests/                      # Unit tests (coming soon)
├── requirements.txt            # Dependencies
├── setup.py                    # Package setup
└── pyproject.toml             # Modern Python packaging
```

## 🔧 API Overview

### LiveConnection

Main interface for Live communication:

```python
live = LiveConnection(
    host="127.0.0.1",
    osc_send_port=11000,
    osc_receive_port=11001,
    scan_on_init=False
)

# Song control
live.play()
live.stop()
live.set_tempo(128.0)

# Track/clip control
live.fire_clip(track_index, clip_index)
live.stop_all_clips()
live.create_midi_track()

# OSC listening
live.start_listening("/live/song/get/beat", callback)
```

### M4LDeviceHelper

Utilities for M4L development:

```python
helper = M4LDeviceHelper(connection)

# MIDI creation
helper.create_note_sequence(track, clip, pitches, duration)
helper.create_drum_pattern(track, clip, pattern)

# Device control
helper.randomize_device_parameters(track, device)
helper.get_device_parameters(track, device)

# Track management
helper.export_track_info(track_index)
helper.setup_basic_scene(num_midi=4, num_audio=2)
```

### Utilities

Musical and conversion utilities:

```python
from live_dev import (
    create_scale,
    midi_note_to_name,
    note_name_to_midi,
    quantize_to_grid,
    beats_to_ms,
    ms_to_beats,
    format_time
)

# Create scales
notes = create_scale(60, "minor")  # C minor
notes = create_scale(67, "pentatonic_major")  # G pentatonic

# Note conversion
name = midi_note_to_name(60)  # "C4"
midi = note_name_to_midi("A#5")  # 82

# Time utilities
formatted = format_time(8.5)  # "3:1:480"
ms = beats_to_ms(4, tempo=120)  # 2000.0
```

## 🧪 Testing

```bash
# Run tests (when available)
pytest

# Run with coverage
pytest --cov=live_dev --cov-report=html
```

## 🔌 Integration with Workspace

This Python integration works seamlessly with other workspace components:

- **Max Live IDE**: Use Python to generate clips that the IDE can visualize
- **Ableton-JS**: Parallel JavaScript control for web-based interfaces
- **LATE**: Automated testing framework for your Live setups

## 🎵 Use Cases

### Generative Music
```python
# Create evolving patterns
import random
from live_dev import create_scale

scale = create_scale(60, "minor")
for _ in range(8):
    melody = [random.choice(scale) for _ in range(16)]
    helper.create_note_sequence(0, _, melody, 0.25)
```

### Performance Controller
```python
# Real-time parameter modulation
def on_beat(beat):
    if beat % 4 == 0:
        helper.randomize_device_parameters(0, 0)

live.start_listening("/live/song/get/beat", on_beat)
```

### Batch Processing
```python
# Process multiple tracks
for i in range(len(live.get_tracks())):
    info = helper.export_track_info(i)
    # Analyze, modify, save...
```

## 📖 Documentation

- [Examples README](examples/README.md) - Detailed example walkthroughs
- [AbletonOSC API](../../AbletonOSC-master/README.md) - Full OSC API reference
- [pylive Docs](../../pylive-master/README.md) - pylive documentation
- [Live Object Model](https://docs.cycling74.com/max8/vignettes/live_object_model) - Official API

## 🛠️ Development

```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ examples/

# Type checking
mypy src/
```

## 🤝 Contributing

This is part of the Live-Dev-Workspace project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [pylive](https://github.com/ideoforms/pylive) by Daniel Jones
- [AbletonOSC](https://github.com/ideoforms/AbletonOSC) by Daniel Jones
- Built for the Live-Dev-Workspace ecosystem

## 🔗 Related Projects

- [Max Live IDE](../max-live-ide/) - Visual Max for Live development
- [Ableton-JS](../ableton-js/) - JavaScript API for Live
- [LATE](../ableton-live-testing/) - Live Automated Testing Environment

---

**Ready to start developing?** Check out the [examples](examples/) directory! 🎵
