#!/usr/bin/env python3
"""
Example README generator for examples
"""


def main():
    readme_content = """# Python Live Development Examples

This directory contains practical examples for using the live-dev-integration package
to control Ableton Live and develop Max for Live devices.

## Prerequisites

1. **Ableton Live 11+** with AbletonOSC installed
2. **Python 3.8+**
3. **Dependencies installed** (see parent directory README)

## Quick Start

1. Install the package in development mode:
   ```bash
   cd ..
   pip install -e .
   ```

2. Make sure AbletonOSC is running in Live:
   - Open Ableton Live
   - Go to Preferences > Link / Tempo / MIDI
   - Set Control Surface to "AbletonOSC"
   - You should see "AbletonOSC: Listening for OSC on port 11000"

3. Run an example:
   ```bash
   python 01_basic_connection.py
   ```

## Examples Overview

### 01_basic_connection.py
**Difficulty: Beginner**

Learn how to:
- Connect to Ableton Live
- Query song tempo
- List tracks and clips
- Get basic set information

```bash
python 01_basic_connection.py
```

### 02_clip_control.py
**Difficulty: Beginner**

Learn how to:
- Start/stop playback
- Fire clips programmatically
- Stop all clips

```bash
python 02_clip_control.py
```

### 03_midi_generation.py
**Difficulty: Intermediate**

Learn how to:
- Create MIDI notes in clips
- Generate melodies from scales
- Create drum patterns
- Work with musical structures

```bash
python 03_midi_generation.py
```

### 04_device_control.py
**Difficulty: Intermediate**

Learn how to:
- Query device parameters
- Randomize parameter values
- Read parameter ranges

```bash
python 04_device_control.py
```

### 05_osc_listeners.py
**Difficulty: Advanced**

Learn how to:
- Listen for real-time OSC events
- React to tempo changes
- Monitor beat events
- Create interactive controllers

```bash
python 05_osc_listeners.py
```

### 06_m4l_template.py
**Difficulty: Advanced**

Learn how to:
- Set up complete Live sessions
- Create track structures
- Build performance controllers
- Export session data

```bash
python 06_m4l_template.py
python 06_m4l_template.py generative  # For generative setup
```

## Common Patterns

### Basic Connection
```python
from live_dev import LiveConnection

with LiveConnection(scan_on_init=True) as live:
    print(f"Tempo: {live.get_tempo()}")
    live.play()
```

### M4L Device Helper
```python
from live_dev import M4LDeviceHelper

helper = M4LDeviceHelper()
helper.create_note_sequence(0, 0, [60, 62, 64, 65])
```

### OSC Listening
```python
def on_beat(beat):
    print(f"Beat: {beat}")

live.start_listening("/live/song/get/beat", on_beat)
```

## Troubleshooting

### "Connection refused" error
- Make sure Ableton Live is running
- Check that AbletonOSC is set as a Control Surface
- Verify ports 11000 and 11001 are not blocked

### "No tracks found"
- Call `live.scan()` to refresh the track list
- Or use `scan_on_init=True` when creating LiveConnection

### "Device not found"
- Make sure the track has devices
- Check the device index (starts at 0)
- Rescan after adding devices: `live.scan()`

## Next Steps

1. Try modifying the examples
2. Combine multiple techniques
3. Build your own Max for Live device
4. Check the API documentation in the main package

## Resources

- [AbletonOSC Documentation](https://github.com/ideoforms/AbletonOSC)
- [pylive Documentation](https://github.com/ideoforms/pylive)
- [Live Object Model](https://docs.cycling74.com/max8/vignettes/live_object_model)
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✓ README.md created")


if __name__ == "__main__":
    main()
