# Live Dev Integration - Quick Reference

## Installation

```bash
cd python
pip install -e .
```

## Basic Usage

### Connect to Live
```python
from live_dev import LiveConnection

with LiveConnection(scan_on_init=True) as live:
    print(f"Tempo: {live.get_tempo()}")
```

### Create MIDI Clips
```python
from live_dev import M4LDeviceHelper, create_scale

helper = M4LDeviceHelper()
scale = create_scale(60, "minor")
helper.create_note_sequence(0, 0, scale, duration=0.25)
```

### Control Devices
```python
helper.randomize_device_parameters(track_index=0, device_index=0)
params = helper.get_device_parameters(0, 0)
```

### Listen to Events
```python
def on_beat(beat):
    print(f"Beat: {beat}")

live.start_listening("/live/song/get/beat", on_beat)
live.send_osc("/live/song/start_listen/beat")
```

## Common Scales

```python
from live_dev import create_scale

create_scale(60, "major")           # C Major
create_scale(60, "minor")           # C Minor
create_scale(60, "pentatonic_major")  # C Pentatonic
create_scale(60, "dorian")          # C Dorian
```

## Utilities

```python
from live_dev import (
    midi_note_to_name,
    note_name_to_midi,
    beats_to_ms,
    quantize_to_grid
)

midi_note_to_name(60)      # "C4"
note_name_to_midi("A#5")   # 82
beats_to_ms(4, tempo=120)  # 2000.0
quantize_to_grid(1.3, 0.25)  # 1.25
```

## Project Structure

```
python/
├── src/live_dev/           # Main package
│   ├── live_connection.py  # Connection manager
│   ├── m4l_helpers.py      # M4L utilities
│   └── utils.py            # Helper functions
├── examples/               # Example scripts
├── requirements.txt        # Dependencies
└── README.md              # Full documentation
```

## Troubleshooting

**Connection refused**
- Start Ableton Live
- Enable AbletonOSC in Preferences

**No tracks found**
- Call `live.scan()` or use `scan_on_init=True`

**Module not found**
- Run `pip install -e .` from python/ directory

## Resources

- [Full Documentation](README.md)
- [Examples](examples/README.md)
- [AbletonOSC API](../AbletonOSC-master/README.md)
