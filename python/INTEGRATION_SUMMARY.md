# Python Integration Summary

## What Was Created

A complete Python integration package that unifies pylive and AbletonOSC for Max for Live device development.

## Directory Structure

```
python/
├── src/live_dev/              # Main package
│   ├── __init__.py            # Package initialization and exports
│   ├── live_connection.py     # Core Live connection manager
│   ├── m4l_helpers.py         # Max for Live device utilities
│   └── utils.py               # Musical and conversion utilities
│
├── examples/                   # Example scripts
│   ├── 01_basic_connection.py # Basic connection and info
│   ├── 02_clip_control.py     # Clip playback control
│   ├── 03_midi_generation.py  # MIDI clip creation
│   ├── 04_device_control.py   # Device parameter control
│   ├── 05_osc_listeners.py    # Real-time event listening
│   ├── 06_m4l_template.py     # M4L device templates
│   ├── create_readme.py       # README generator
│   └── README.md              # Examples documentation
│
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation (traditional)
├── pyproject.toml             # Modern Python packaging
├── README.md                   # Complete documentation
├── QUICKREF.md                # Quick reference guide
├── .env.example               # Configuration template
├── .gitignore                 # Git ignore patterns
├── install.sh                 # Unix installation script
├── install.bat                # Windows installation script
└── quickstart.py              # Setup verification script
```

## Key Features

### 1. LiveConnection Class
- Unified interface to Ableton Live
- Combines pylive's high-level API with AbletonOSC's OSC control
- Context manager support for clean resource handling
- Real-time OSC event listening

### 2. M4LDeviceHelper Class
- Specialized utilities for Max for Live device development
- MIDI clip creation (melodies, drum patterns)
- Device parameter randomization and control
- Track information export
- Scene setup automation

### 3. Utility Functions
- Musical scale generation (major, minor, pentatonic, modes)
- MIDI note conversion (number ↔ name)
- Time conversion (beats ↔ milliseconds)
- Quantization utilities
- Colored logging with multiple output levels

## Installation Methods

### Method 1: Quick Install (Recommended)
```bash
cd python
./install.sh  # macOS/Linux
# or
install.bat   # Windows
```

### Method 2: Manual Install
```bash
cd python
pip install -e .
```

### Method 3: Requirements Only
```bash
cd python
pip install -r requirements.txt
```

## Getting Started

1. **Verify Setup**
   ```bash
   cd python
   python3 quickstart.py
   ```

2. **Run First Example**
   ```bash
   cd examples
   python3 01_basic_connection.py
   ```

3. **Read Documentation**
   - `README.md` - Full API documentation
   - `examples/README.md` - Example walkthroughs
   - `QUICKREF.md` - Quick reference

## Integration with Workspace

The Python integration complements existing workspace components:

### With AbletonOSC-master/
- Uses AbletonOSC as the underlying OSC communication layer
- Provides high-level Python wrapper around OSC commands
- Access to full Live Object Model API

### With pylive-master/
- Integrates pylive's track/clip/device classes
- Adds convenience methods and M4L-specific helpers
- Maintains compatibility with pylive patterns

### With max-live-ide/
- Python can generate MIDI clips for IDE visualization
- Backend processing for complex operations
- Automation and testing support

### With ableton-live-testing/
- Shared testing infrastructure
- Python can be used to create test fixtures
- Automated Live Set validation

## Example Use Cases

### 1. Generative Music Device
```python
from live_dev import M4LDeviceHelper, create_scale
import random

helper = M4LDeviceHelper()
scale = create_scale(60, "minor")

for clip in range(8):
    melody = [random.choice(scale) for _ in range(16)]
    helper.create_note_sequence(0, clip, melody, 0.25)
```

### 2. Performance Controller
```python
from live_dev import LiveConnection

def on_beat(beat):
    if beat % 16 == 0:  # Every bar
        live.send_osc("/live/scene/fire", beat // 16)

with LiveConnection() as live:
    live.start_listening("/live/song/get/beat", on_beat)
    live.send_osc("/live/song/start_listen/beat")
    # Keep running...
```

### 3. Device Parameter Automator
```python
from live_dev import M4LDeviceHelper

helper = M4LDeviceHelper()

# Get all parameters
params = helper.get_device_parameters(0, 0)

# Create automation pattern
for param_name in params:
    if "Cutoff" in param_name:
        # Modulate cutoff frequency
        values = [0.0, 0.5, 1.0, 0.5]
        helper.modulate_parameter(0, 0, param_name, values)
```

## Dependencies

### Core Dependencies
- `pylive>=0.4.0` - High-level Live API
- `python-osc>=1.8.0` - OSC communication
- `python-dotenv>=1.0.0` - Environment configuration
- `colorama>=0.4.6` - Colored terminal output

### Optional Dependencies
- `pytest>=7.4.0` - Testing framework
- `mido>=1.3.0` - Advanced MIDI support
- `numpy>=1.24.0` - Audio processing

## Configuration

Environment variables (create `.env` from `.env.example`):

```bash
LIVE_HOST=127.0.0.1
LIVE_OSC_SEND_PORT=11000
LIVE_OSC_RECEIVE_PORT=11001
LOG_LEVEL=INFO
SCAN_ON_INIT=true
```

## Testing

```bash
# Verify installation
python3 quickstart.py

# Test basic connection (requires Live running)
python3 examples/01_basic_connection.py

# Run unit tests (when available)
pytest tests/
```

## Next Steps

1. **Explore Examples**: Work through all 6 examples to understand capabilities
2. **Read API Docs**: Review README.md for comprehensive API documentation
3. **Build M4L Device**: Use the integration to build your Max for Live device
4. **Integrate with IDE**: Combine Python backend with Max Live IDE frontend
5. **Create Templates**: Save your common patterns as reusable templates

## Troubleshooting

### Import Errors
```bash
# Reinstall package
pip install -e . --force-reinstall
```

### Connection Issues
1. Check Ableton Live is running
2. Verify AbletonOSC is enabled (Preferences > MIDI)
3. Test with: `python3 quickstart.py`

### Module Not Found
```bash
# Check installation
pip list | grep live-dev
# Should show: live-dev-integration

# Reinstall if missing
pip install -e .
```

## Resources

- [AbletonOSC Documentation](../AbletonOSC-master/README.md)
- [pylive Documentation](../pylive-master/README.md)
- [Live Object Model](https://docs.cycling74.com/max8/vignettes/live_object_model)
- [Python OSC Docs](https://python-osc.readthedocs.io/)

## Contributing

To contribute to the Python integration:

1. Add new utilities to `src/live_dev/utils.py`
2. Extend helpers in `src/live_dev/m4l_helpers.py`
3. Create examples in `examples/`
4. Update documentation in `README.md`
5. Add tests in `tests/` (when test suite is created)

## Maintenance

### Adding New Features
1. Implement in appropriate module
2. Add example demonstrating usage
3. Update README.md with API documentation
4. Update QUICKREF.md if commonly used

### Version Updates
1. Update `__version__` in `src/live_dev/__init__.py`
2. Update `version` in `setup.py` and `pyproject.toml`
3. Update changelog (when created)
4. Tag release in git

---

**Integration Complete!** 🎵

The Python integration is now fully set up and ready for Max for Live device development.
