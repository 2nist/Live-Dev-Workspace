# Python Integration for M4L Development

## Quick Start

The Python integration provides a unified API for controlling Ableton Live and developing Max for Live devices.

### Installation

```bash
cd python
./install.sh  # macOS/Linux
# or
install.bat   # Windows
```

### First Steps

```bash
# Verify installation
python3 quickstart.py

# Run first example
cd examples
python3 01_basic_connection.py
```

## What's Included

- **LiveConnection**: Unified Live control API
- **M4LDeviceHelper**: Max for Live device utilities
- **6 Complete Examples**: From basic to advanced
- **Musical Utilities**: Scales, conversions, quantization

## Documentation

- [Full Documentation](python/README.md)
- [Quick Reference](python/QUICKREF.md)
- [Examples Guide](python/examples/README.md)
- [Integration Summary](python/INTEGRATION_SUMMARY.md)

## Example Usage

```python
from live_dev import LiveConnection, M4LDeviceHelper, create_scale

# Connect to Live
with LiveConnection(scan_on_init=True) as live:
    # Control playback
    live.play()
    live.set_tempo(128)
    
    # Create MIDI clips
    helper = M4LDeviceHelper(live)
    scale = create_scale(60, "minor")
    helper.create_note_sequence(0, 0, scale, duration=0.25)
```

## Integration Architecture

```
Live-Dev-Workspace/
├── python/                    # Python integration ⭐ NEW
│   ├── src/live_dev/         # Core package
│   ├── examples/             # Example scripts
│   └── README.md             # Full documentation
│
├── AbletonOSC-master/        # OSC communication layer
├── pylive-master/            # High-level Live API
├── max-live-ide/             # Visual M4L development
└── ableton-live-testing/     # Testing framework
```

The Python integration unifies AbletonOSC and pylive, making them easier to use for M4L device development.

## Resources

- [Python Package README](python/README.md) - Complete API documentation
- [AbletonOSC README](AbletonOSC-master/README.md) - OSC API reference  
- [pylive README](pylive-master/README.md) - pylive documentation

---

Ready to build your Max for Live device with Python! 🎵
