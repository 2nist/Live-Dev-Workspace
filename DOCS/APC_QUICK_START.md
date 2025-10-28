# APC64 & APC mini mk2 Quick Start Guide

## 🎛️ Your Controllers

### Akai APC64
- **64 RGB Pads** (8x8 grid)
- **8 Encoders** with LED rings
- **8 Channel Faders** (60mm)
- **Master Fader**
- **Dedicated transport controls**
- **Note Mode** for melodic playing
- **USB MIDI** connectivity

### Akai APC mini mk2  
- **64 RGB Pads** (8x8 grid)
- **8 Channel Faders** (25mm)
- **Compact design** (7.5" x 7.9")
- **USB MIDI** connectivity
- **Class-compliant** (no drivers needed)

---

## 🚀 Quick Setup

### 1. Connect Hardware

```bash
# Plug in your APC via USB
# Controllers are class-compliant, no drivers needed on macOS/Linux
```

### 2. Start Arranger System

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/python
python -m arranger.live_bridge.osc_server
```

### 3. Launch Max Live IDE

```bash
cd /Users/Matthew/Live_Dev/Live-Dev-Workspace/max-live-ide
npm start
```

### 4. Connect Controller

```javascript
// In Max Live IDE Hardware Panel:
1. Click "Scan for Controllers"
2. You should see:
   - "Akai APC64" or
   - "Akai APC mini mk2"
3. Click "Connect"
4. Pads will light up to confirm connection
```

---

## 🎵 Pad Layout

### APC64 & APC mini mk2 Grid

```
Top Row (Notes 56-63):      ██ ██ ██ ██ ██ ██ ██ ██  
                            ██ ██ ██ ██ ██ ██ ██ ██
                            ██ ██ ██ ██ ██ ██ ██ ██
                            ██ ██ ██ ██ ██ ██ ██ ██
                            ██ ██ ██ ██ ██ ██ ██ ██
                            ██ ██ ██ ██ ██ ██ ██ ██
                            ██ ██ ██ ██ ██ ██ ██ ██
Bottom Row (Notes 0-7):     ██ ██ ██ ██ ██ ██ ██ ██
```

**MIDI Layout:**
- **APC64:** Bottom-to-top (note 0 = bottom-left, note 63 = top-right)
- **APC mini mk2:** Top-to-bottom (note 0 = top-left, note 63 = bottom-right)

---

## 🎨 Color Palette

### Velocity-Based RGB Colors

| Velocity | Color | Use Case |
|----------|-------|----------|
| 0 | Off | Empty/inactive |
| 1-5 | Red (dim→bright) | Minor chords, errors |
| 6-11 | Orange | Dominant chords |
| 12-16 | Yellow | Augmented, warnings |
| 17-21 | Green | Major chords, active |
| 22-26 | Cyan | Scales, info |
| 27-31 | Blue | Sections, backgrounds |
| 32-36 | Purple | Diminished, special |
| 37+ | White/Mixed | Playing, highlights |

---

## 🎼 Chord Progression Mode

### Layout (Your APC64/mini mk2)

```
Rows 1-2 (Top):     🎵 Chord Progression (16 chords max)
                    [Cmaj7] [Dm7] [G7] [Cmaj7] ...

Rows 3-6:           🎹 Chord Variations
                    [Root] [1st Inv] [2nd Inv] [Add9] ...

Rows 7-8 (Bottom):  🎛️ Transport Controls
                    [Play] [Stop] [Rec] [Modes] ...
```

### Example: Jazz ii-V-I

```javascript
const progression = [
  { root: 'D', quality: 'm7' },   // Green (pad 0)
  { root: 'G', quality: '7' },    // Orange (pad 1)
  { root: 'C', quality: 'maj7' }  // Green (pad 2)
];

await osc.sendHardwareCommand('set_mode', { mode: 'chord' });
await osc.sendHardwareCommand('display_progression', { chords: progression });
```

**Result on APC64:**
- Pad 0 (bottom-left): **Blue** (Dm7)
- Pad 1: **Orange** (G7)
- Pad 2: **Green** (Cmaj7)

---

## 📋 Section/Arrangement Mode

### Your Song Structure Visualized

```
[Intro]  [Verse1] [Chorus] [Verse2] [Chorus] [Bridge] [Chorus] [Outro]
  🔵       🟢       🔴       🟢       🔴       🟠       🔴       ⚫
```

### Example: Build a Track

```javascript
const arrangement = {
  sections: [
    { name: 'Intro', duration: 8, chords: [...] },    // Pad 0 = Blue
    { name: 'Verse 1', duration: 16, chords: [...] }, // Pad 1 = Green
    { name: 'Chorus', duration: 16, chords: [...] },  // Pad 2 = Red
    { name: 'Drop', duration: 8, chords: [...] }      // Pad 3 = Purple
  ]
};

await osc.sendHardwareCommand('set_mode', { mode: 'section' });
await osc.sendHardwareCommand('display_arrangement', arrangement);
```

**Navigation:**
- Each pad = one section
- Press pad to jump (coming soon)
- Bright = currently playing

---

## 🎹 Scale Mode

### Keyboard Layout on Pads

```
C# D# ·  F# G# A# ·      (Chromatic - dim)
██ ██ ░░ ██ ██ ██ ░░   
C  D  E  F  G  A  B      (C Major scale - bright)
```

### Example: C Minor Pentatonic

```javascript
// Display C minor pentatonic scale
await osc.sendHardwareCommand('set_mode', { mode: 'scale' });

const bridge = get_hardware_bridge();
bridge.display_scale(
  60,                    // Root = C (MIDI 60)
  [0, 3, 5, 7, 10]      // Min pentatonic intervals
);
```

**Result:**
- C, Eb, F, G, Bb = **Bright**
- Other notes = **Dim**

---

## 🎚️ Fader Control (Coming Soon)

### APC64 (8 Faders)
- Fader 1-8: Track volumes
- Master fader: Overall level

### APC mini mk2 (8 Faders)
- Fader 1-8: Track volumes or parameters

```python
# Set fader position
controller.set_fader(0, 100)  # Fader 1 to 100/127
```

---

## 🔧 Workflow Examples

### 1. AI-Assisted Composition

```javascript
// Generate chords with AI
const aiChords = await ai.generateFromNaturalLanguage(
  "create a dark techno progression in A minor"
);

// Display on your APC
await osc.sendHardwareCommand('display_progression', { 
  chords: aiChords 
});

// See colors:
// - Blue pads = minor chords
// - Orange = dominant tension
// - Purple = diminished/dark
```

### 2. Live Performance Setup

```javascript
// Load arrangement
await osc.sendHardwareCommand('set_mode', { mode: 'section' });
await osc.sendHardwareCommand('display_arrangement', myTrack);

// Your APC now shows:
// Row 1: [Intro] [Build] [Drop] [Break] ...
// Each pad triggers that section in Live
```

### 3. Scale Practice

```javascript
// Practice scales on your APC
await osc.sendHardwareCommand('set_mode', { mode: 'scale' });

// Cycle through scales
const scales = ['major', 'minor', 'dorian', 'phrygian'];
for (let scale of scales) {
  bridge.display_scale(60, getScaleIntervals(scale));
  await sleep(5000); // 5 seconds each
}
```

---

## 💡 Pro Tips

### For APC64 Users

1. **Use encoders** for parameter control (coming soon)
2. **Dedicated transport** buttons for workflow
3. **Larger faders** = better mixing control
4. **Note mode** for playing melodies

### For APC mini mk2 Users

1. **Compact size** = perfect for laptop producers
2. **USB bus powered** = no external power
3. **8 faders** for quick volume control
4. **Portable** = take it anywhere

### Both Controllers

1. **Color feedback** shows what's happening
2. **8x8 grid** = perfect for 16-step sequencing
3. **RGB pads** = customize your workflow
4. **MIDI over USB** = low latency

---

## 🐛 Troubleshooting

### APC Not Detected

```bash
# Check MIDI ports
python -c "import mido; print(mido.get_input_names())"

# Should show:
# - "APC64" or
# - "APC mini mk2"
```

### Pads Not Lighting

```python
# Test individual pad
from arranger.hardware import get_controller_manager, APCController

manager = get_controller_manager()
apc = APCController('APC64', 'APC64', 'apc64')
manager.add_controller('my_apc', apc)

# Light first pad red
apc.set_pad_color(0, (127, 0, 0))

# Clear all
apc.clear_all_pads()
```

### Connection Issues

1. **Unplug and reconnect** USB
2. **Close Ableton Live** (releases MIDI ports)
3. **Restart arranger server**
4. **Check USB cable** (try different port)

---

## 📖 Next Steps

- [Full Hardware Guide](./HARDWARE_CONTROLLER_GUIDE.md)
- [Development Guide](../DEVELOPMENT_GUIDE.md)
- [Quick Reference](./HARDWARE_QUICK_REFERENCE.md)

---

## 🎵 Complete Example

```javascript
// 1. Connect your APC
await osc.sendHardwareCommand('connect', {
  type: 'apc64',  // or 'apc_mini_mk2'
  midiIn: 'APC64',
  midiOut: 'APC64'
});

// 2. AI generates progression
const chords = await ai.generateFromNaturalLanguage(
  "create a chill lofi progression in C major"
);

// 3. Display on hardware
await osc.sendHardwareCommand('display_progression', { chords });

// 4. Watch pads light up:
// Green = Cmaj7
// Blue = Am7
// Orange = Dm7 → G7

// 5. Build arrangement
const track = {
  sections: [
    { name: 'Intro', chords: chords.slice(0, 2) },
    { name: 'Verse', chords: chords },
    { name: 'Chorus', chords: chorusChords }
  ]
};

// 6. Switch to section mode
await osc.sendHardwareCommand('set_mode', { mode: 'section' });
await osc.sendHardwareCommand('display_arrangement', track);

// 7. Send to Live
await liveIntegration.createScenes(track);

// Result: Complete track on your APC! 🎉
```

---

**Your APC64/mini mk2 is now a music theory visualization and composition tool! 🎛️🎵**
