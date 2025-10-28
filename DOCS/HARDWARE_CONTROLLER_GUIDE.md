# Hardware Controller Integration Guide

## Overview

The Arranger System now supports **Ableton hardware controllers** including Push 2/3, Launchpad, and other MIDI surfaces. This integration allows you to:

- **Visualize chord progressions** on hardware pads with color coding
- **Display arrangement sections** with intelligent layout
- **Control playback** and navigate your music from hardware
- **AI-assisted composition** with tactile feedback
- **Scale visualization** for performance and composition

---

## Supported Controllers

### ✅ Officially Supported

| Controller | Status | Features |
|------------|--------|----------|
| **Akai APC64** | ✅ Full Support | 64 RGB pads, 8 encoders, 8 faders |
| **Akai APC mini mk2** | ✅ Full Support | 64 RGB pads, 8 faders, compact design |
| **Ableton Push 2** | ✅ Full Support | 64 RGB pads, 8 encoders, LCD display |
| **Ableton Push 3** | ✅ Full Support | 64 RGB pads, 8 encoders, color display, MPE |
| **Launchpad Pro** | ✅ Full Support | 64 RGB pads, programmer mode |
| **Launchpad X** | ✅ Full Support | 64 RGB pads, custom lighting |
| **Launchpad Mini** | ✅ Supported | 64 pads, simplified layout |

### 🔄 Coming Soon

- APC40 / APC40 mkII
- APC Key 25
- Generic MIDI controllers (custom mapping)

---

## Installation

### 1. Install Python Dependencies

```bash
cd python
pip install mido python-rtmidi
```

**MIDI Library Installation:**

**macOS:**
```bash
brew install portmidi
pip install python-rtmidi
```

**Windows:**
```bash
# python-rtmidi includes Windows binaries
pip install python-rtmidi
```

**Linux:**
```bash
sudo apt-get install libasound2-dev libjack-dev
pip install python-rtmidi
```

### 2. Configure Live

Ensure **AbletonOSC** is running and connected to Live:

```python
# In your arranger OSC server
server = ArrangerOSCServer(
    ip="127.0.0.1",
    port=12000,
    use_live=True,  # Enable Live connection
    ableton_port=11000
)
```

### 3. Connect Hardware Controller

**Option A: Auto-Detection (Recommended)**

The system will automatically detect connected controllers:

```javascript
// In Max Live IDE
const hardware = useHardwareControllers();
await hardware.detectControllers();
// Displays detected controllers with "Connect" buttons
```

**Option B: Manual Connection**

```javascript
// Connect specific controller
await hardware.connectController({
  type: 'push2',
  midiIn: 'Ableton Push 2 User Port',
  midiOut: 'Ableton Push 2 User Port'
});
```

---

## Usage Guide

### Quick Start (Max Live IDE)

1. **Open Max Live IDE**
2. **Navigate to Hardware Panel** (bottom right)
3. **Click "Scan for Controllers"**
4. **Select detected controller** and click "Connect"
5. **Choose display mode:**
   - 🎵 Chord Progression
   - 📋 Arrangement Sections
   - 🎹 Scale Layout

### Display Modes

#### 🎵 Chord Progression Mode

Displays your chord progression on the controller pads:

**Layout (8x8 grid):**
```
[Row 1-2] Chord progression (up to 16 chords)
  - Green = Major chords
  - Blue = Minor chords
  - Orange = Dominant chords
  - Purple = Diminished
  - Yellow = Augmented

[Row 3-6] Chord variations/voicings
  - Root position
  - Inversions
  - Extensions (9th, 11th, 13th)
  - Suspensions

[Row 7-8] Transport controls
  - Play/Stop
  - Record
  - Mode switching
```

**Color Coding:**
- **Bright** = Current chord
- **Dim** = Available chords
- **Flashing** = Playing

**Example:**
```javascript
// Connect APC64
await hardware.connectController({
  type: 'apc64',
  midiIn: 'APC64',
  midiOut: 'APC64'
});

// Connect APC mini mk2
await hardware.connectController({
  type: 'apc_mini_mk2',
  midiIn: 'APC mini mk2',
  midiOut: 'APC mini mk2'
});

// Display progression on hardware
await hardware.displayProgression([
  { symbol: 'Cmaj7', notes: [60, 64, 67, 71] },
  { symbol: 'Dm7', notes: [62, 65, 69, 72] },
  { symbol: 'G7', notes: [67, 71, 74, 77] },
  { symbol: 'Cmaj7', notes: [60, 64, 67, 71] }
]);

// Highlight playing chord
await hardware.highlightChord(2); // Highlight G7
```

#### 📋 Arrangement Sections Mode

Displays your song structure:

**Layout:**
```
Each pad = One section
Colors indicate section type:
  - Light Blue = Intro
  - Green = Verse
  - Red = Chorus
  - Orange = Bridge
  - Gray = Outro
  - Purple = Drop
  - Cyan = Breakdown
```

**Brightness:**
- **Bright** = Currently playing
- **Medium** = Available sections
- **Dim** = Completed sections

**Example:**
```javascript
// Display arrangement
await hardware.displayArrangement({
  sections: [
    { name: 'Intro', duration: 8, chords: [...] },
    { name: 'Verse 1', duration: 16, chords: [...] },
    { name: 'Chorus', duration: 16, chords: [...] }
  ]
});
```

#### 🎹 Scale Layout Mode

Keyboard-style scale visualization:

**Layout:**
```
Chromatic layout with scale highlighting:
  - Bright Green = Root note
  - Bright Orange = Fifth (dominant)
  - Blue = Fourth (subdominant)
  - Medium Blue = Other scale tones
  - Dim Gray = Chromatic (out-of-scale)
```

**Use Cases:**
- Composition within a scale
- Performance mode
- Note visualization
- Learning scales

---

## API Reference

### Python Backend

#### Controller Manager

```python
from arranger.hardware import get_controller_manager

# Get manager instance
manager = get_controller_manager()

# Auto-detect controllers
detected = manager.auto_detect_controllers()
# Returns: [{'name': 'push2', 'port': 'Ableton Push 2 User Port', ...}]

# Add controller manually
from arranger.hardware import PushController
push = PushController(
    midi_in='Ableton Push 2 User Port',
    midi_out='Ableton Push 2 User Port',
    version=2
)
manager.add_controller('my_push', push)

# List connected controllers
controllers = manager.list_controllers()

# Set active controller
manager.set_active_controller('my_push')
```

#### Hardware Bridge

```python
from arranger.hardware import get_hardware_bridge

bridge = get_hardware_bridge()

# Initialize and detect
bridge.initialize()

# Set display mode
bridge.set_mode('chord')  # or 'section', 'scale'

# Display chord progression
from arranger.models.chord import Chord
chords = [
    Chord(root='C', quality='maj7', duration=4.0),
    Chord(root='D', quality='m7', duration=4.0)
]
bridge.display_chord_progression(chords)

# Highlight playing chord
bridge.highlight_playing_chord(0)  # First chord

# Display arrangement
from arranger.models.arrangement import Arrangement
bridge.display_arrangement(my_arrangement)
```

### OSC Endpoints

All hardware endpoints are available via OSC on port **12000**:

#### `/hardware/detect`
Auto-detect connected controllers.

**Returns:**
```json
{
  "detected": [
    {
      "name": "push2",
      "type": "Ableton Push 2",
      "port": "Ableton Push 2 User Port"
    }
  ]
}
```

#### `/hardware/connect <type> <midi_in> <midi_out>`
Connect to a hardware controller.

**Parameters:**
- `type`: Controller type (push2, push3, launchpad_pro, etc.)
- `midi_in`: MIDI input port name
- `midi_out`: MIDI output port name

**Example:**
```
/hardware/connect push2 "Ableton Push 2 User Port" "Ableton Push 2 User Port"
```

#### `/hardware/set_mode <mode>`
Change display mode.

**Parameters:**
- `mode`: "chord", "section", or "scale"

#### `/hardware/display_progression <chords_json>`
Display chord progression on controller.

**Parameters:**
- `chords_json`: JSON array of chord objects

**Example:**
```json
[
  {"root": "C", "quality": "maj7", "notes": [60, 64, 67, 71]},
  {"root": "D", "quality": "m7", "notes": [62, 65, 69, 72]}
]
```

#### `/hardware/highlight_chord <index>`
Highlight a chord in the progression.

**Parameters:**
- `index`: Chord index (0-based)

### React (Max Live IDE)

#### HardwareControllerPanel Component

```javascript
import HardwareControllerPanel from './components/HardwareControllerPanel';

function App() {
  const [arrangement, setArrangement] = useState(null);
  const [progression, setProgression] = useState([]);

  return (
    <HardwareControllerPanel
      currentArrangement={arrangement}
      currentProgression={progression}
    />
  );
}
```

#### ArrangerOSC Utility

```javascript
import { getArrangerOSC } from './utils/ArrangerOSC';

const osc = getArrangerOSC();

// Detect controllers
const result = await osc.sendHardwareCommand('detect');
console.log(result.detected);

// Connect controller
await osc.sendHardwareCommand('connect', {
  type: 'push2',
  midiIn: 'Ableton Push 2 User Port',
  midiOut: 'Ableton Push 2 User Port'
});

// Change mode
await osc.sendHardwareCommand('set_mode', { mode: 'chord' });

// Display progression
await osc.sendHardwareCommand('display_progression', {
  chords: myChords
});

// Highlight chord
await osc.sendHardwareCommand('highlight_chord', { index: 0 });
```

---

## Advanced Features

### Custom Color Schemes

```python
# In hardware_bridge.py, customize PadMapping.COLORS

PadMapping.COLORS = {
    "major": (0, 255, 0),     # Bright green
    "minor": (0, 0, 255),      # Bright blue
    "dominant": (255, 100, 0), # Orange
    # ... customize all colors
}
```

### Bidirectional Control

**Receive pad presses from hardware:**

```python
def on_pad_press(pad_index, velocity):
    print(f"Pad {pad_index} pressed with velocity {velocity}")
    # Trigger chord, change section, etc.

controller.on_pad_press(on_pad_press)
```

### Multi-Controller Support

```python
# Connect multiple controllers
manager.add_controller('push', push_controller)
manager.add_controller('launchpad', launchpad_controller)

# Switch between them
manager.set_active_controller('push')
# ... use push
manager.set_active_controller('launchpad')
# ... use launchpad
```

---

## Troubleshooting

### Controller Not Detected

**Check MIDI ports:**
```python
import mido
print(mido.get_input_names())
print(mido.get_output_names())
```

**Ensure controller is in correct mode:**
- **Push 2/3:** Should be in "User Mode" (set automatically)
- **Launchpad:** Should be in "Programmer Mode" (set automatically)

### Connection Fails

1. **Close other applications** using the controller (Ableton Live, etc.)
2. **Restart controller** (unplug/replug USB)
3. **Check driver installation** (Windows may need drivers)
4. **Verify port names** match exactly

### Pads Not Lighting Up

1. **Check controller mode** is set correctly
2. **Verify controller is active:**
   ```python
   active = manager.get_active_controller()
   print(active.connected)
   ```
3. **Try manual color test:**
   ```python
   controller.set_pad_color(0, (127, 0, 0))  # Red first pad
   ```

### Performance Issues

- **Reduce update frequency** when syncing to Live
- **Use batch updates** instead of individual pad updates
- **Lower color resolution** if needed (use simpler colors)

---

## Examples

### Example 1: Chord Progression Visualizer

```python
from arranger.hardware import get_hardware_bridge
from arranger.models.chord import Chord

bridge = get_hardware_bridge()
bridge.initialize()
bridge.set_mode('chord')

# I-IV-V-I progression
progression = [
    Chord(root='C', quality='maj7', duration=4.0),
    Chord(root='F', quality='maj7', duration=4.0),
    Chord(root='G', quality='7', duration=4.0),
    Chord(root='C', quality='maj7', duration=4.0)
]

bridge.display_chord_progression(progression)

# Animate playback
import time
for i, chord in enumerate(progression):
    bridge.highlight_playing_chord(i)
    time.sleep(4)  # Hold for 4 beats
```

### Example 2: Interactive Section Navigator

```javascript
// React component
function SectionNavigator() {
  const [sections, setSections] = useState([...]);
  const [currentSection, setCurrentSection] = useState(0);
  const osc = getArrangerOSC();

  useEffect(() => {
    // Display arrangement on hardware
    osc.sendHardwareCommand('set_mode', { mode: 'section' });
    osc.sendHardwareCommand('display_arrangement', {
      sections: sections
    });
  }, [sections]);

  const jumpToSection = (index) => {
    setCurrentSection(index);
    osc.sendHardwareCommand('highlight_section', { index });
    // Trigger playback in Live...
  };

  return (
    <div>
      {sections.map((section, i) => (
        <button onClick={() => jumpToSection(i)}>
          {section.name}
        </button>
      ))}
    </div>
  );
}
```

### Example 3: AI Chord Suggestions with Hardware

```javascript
// Get AI chord suggestions and display on hardware
async function generateNextChord(currentChord) {
  const ai = getAIService();
  
  // Get AI suggestions
  const suggestions = await ai.getSuggestions(
    `suggest next chords after ${currentChord}`
  );
  
  // Parse and display on hardware
  const chords = parseChordSuggestions(suggestions);
  await osc.sendHardwareCommand('display_progression', {
    chords: chords
  });
  
  // Highlight current
  await osc.sendHardwareCommand('highlight_chord', { index: 0 });
}
```

---

## Roadmap

### Phase 1 (Current Release) ✅
- Push 2/3 support
- Launchpad Pro/X/Mini support
- Chord progression display
- Section display
- Basic color coding

### Phase 2 (Next Release) 🔄
- **Bidirectional control** (receive pad presses)
- **Encoder mapping** for parameters
- **Transport control** from hardware
- **Live clip launching** from pads

### Phase 3 (Future) 🚀
- **APC40 support**
- **Custom MIDI mapping**
- **Multi-controller sync**
- **Hardware-driven AI composition**
- **Performance mode** with arpeggiation
- **Preset management** on hardware

---

## Contributing

Found a bug or want to add support for a new controller?

1. **Open an issue** describing the hardware
2. **Provide MIDI specifications** if available
3. **Test with mock mode** first
4. **Submit pull request** with controller class

### Adding a New Controller

```python
# In controller_manager.py

class MyController(HardwareController):
    def __init__(self, midi_in, midi_out):
        super().__init__(
            ControllerType.GENERIC_MIDI,
            midi_in,
            midi_out
        )
        
    def _initialize_controller(self):
        # Send initialization SysEx messages
        pass
        
    def set_pad_color(self, pad_index, color):
        # Implement color setting for your hardware
        pass
        
    def clear_all_pads(self):
        # Clear all LEDs
        pass
```

---

## License

Hardware controller integration is part of the Arranger System and follows the same license.

**Supported Controller Trademarks:**
- Ableton Push is a trademark of Ableton AG
- Launchpad is a trademark of Focusrite Audio Engineering Ltd
- This project is not affiliated with or endorsed by these companies

---

## Support

- **Documentation:** [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)
- **Issues:** GitHub Issues
- **Discord:** [Join our community](#)

**Happy composing with hardware! 🎛️🎵**
