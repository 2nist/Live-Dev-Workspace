# Hardware Controller Quick Reference

## 🚀 Quick Start

### 1. Connect Your Controller

```bash
# Start arranger OSC server with hardware support
cd python
python -m arranger.live_bridge.osc_server
```

```javascript
// In Max Live IDE
1. Open Hardware Panel (bottom right)
2. Click "Scan for Controllers"
3. Click "Connect" on detected controller
4. Choose display mode (Chord/Section/Scale)
```

---

## 🎵 Chord Progression Mode

### Pad Layout (Push 2/3, Launchpad)

```
Row 1-2:  ██ ██ ██ ██ ██ ██ ██ ██    Chord Progression (16 max)
          ██ ██ ██ ██ ██ ██ ██ ██    
          
Row 3-6:  ░░ ░░ ░░ ░░ ░░ ░░ ░░ ░░    Chord Variations
          ░░ ░░ ░░ ░░ ░░ ░░ ░░ ░░    (Inversions, Extensions)
          ░░ ░░ ░░ ░░ ░░ ░░ ░░ ░░    
          ░░ ░░ ░░ ░░ ░░ ░░ ░░ ░░    

Row 7-8:  ▓▓ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓    Transport/Controls
          ▓▓ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓    
```

### Color Code

| Color | Chord Type |
|-------|------------|
| 🟢 Green | Major (maj, maj7, maj9) |
| 🔵 Blue | Minor (m, m7, m9) |
| 🟠 Orange | Dominant (7, 9, 13) |
| 🟣 Purple | Diminished (dim, m7♭5) |
| 🟡 Yellow | Augmented (aug) |
| ⚪ White | Currently Playing |

### Workflow

```javascript
// 1. Create progression
const progression = [
  { root: 'C', quality: 'maj7' },
  { root: 'F', quality: 'maj7' },
  { root: 'G', quality: '7' },
  { root: 'C', quality: 'maj7' }
];

// 2. Display on hardware
await osc.sendHardwareCommand('display_progression', { chords: progression });

// 3. Highlight as you play
await osc.sendHardwareCommand('highlight_chord', { index: 0 });
```

---

## 📋 Section Mode

### Layout

```
Each pad = One arrangement section

Intro    Verse1   Chorus   Verse2   Chorus   Bridge   Chorus   Outro
 🔵       🟢       🔴       🟢       🔴       🟠       🔴       ⚫

(Colors indicate section type, brightness = playing state)
```

### Color Code

| Color | Section Type |
|-------|--------------|
| 🔵 Light Blue | Intro |
| 🟢 Green | Verse |
| 🔴 Red | Chorus |
| 🟠 Orange | Bridge |
| ⚫ Gray | Outro |
| 🟣 Purple | Drop/Build |
| 🔷 Cyan | Breakdown |

### Workflow

```javascript
// Display arrangement
await osc.sendHardwareCommand('display_arrangement', {
  sections: [
    { name: 'Intro', duration: 8, chords: [...] },
    { name: 'Verse 1', duration: 16, chords: [...] },
    { name: 'Chorus', duration: 16, chords: [...] }
  ]
});

// Navigate sections
await osc.sendHardwareCommand('highlight_section', { index: 1 });
```

---

## 🎹 Scale Mode

### Layout

```
Chromatic keyboard layout with scale highlighting:

C# D# ·  F# G# A# ·     (Chromatic - dim)
██ ██ ░░ ██ ██ ██ ░░   
C  D  E  F  G  A  B     (Scale tones - bright)
```

### Color Code

| Brightness | Note Type |
|------------|-----------|
| 🟢 Bright Green | Root (tonic) |
| 🟠 Orange | Fifth (dominant) |
| 🔵 Blue | Fourth (subdominant) |
| 🔷 Medium Blue | Other scale tones |
| ⚫ Dim Gray | Chromatic (out-of-scale) |

### Workflow

```javascript
// Display C major scale
await osc.sendHardwareCommand('set_mode', { mode: 'scale' });
await bridge.display_scale(60, [0, 2, 4, 5, 7, 9, 11]);
```

---

## 🎛️ Push-Specific Features

### Display Integration (Push 2/3)

```python
# Show text on Push display
if controller.capabilities.has_display:
    controller.display_text(0, "I - IV - V - I")
    controller.display_text(1, "C - F - G - C")
```

### Encoders

```python
# Map encoders to parameters (coming soon)
# encoder[0] = Tempo
# encoder[1] = Swing
# encoder[2] = Velocity
# encoder[3-7] = Chord parameters
```

### Touchstrip

```python
# Pitch bend, modulation (coming soon)
```

---

## 🔧 Common Tasks

### Switch Modes

```javascript
// Chord mode
await osc.sendHardwareCommand('set_mode', { mode: 'chord' });

// Section mode
await osc.sendHardwareCommand('set_mode', { mode: 'section' });

// Scale mode
await osc.sendHardwareCommand('set_mode', { mode: 'scale' });
```

### Auto-Sync with Playback

```javascript
// Enable auto-sync in UI
<HardwareControllerPanel
  currentProgression={progression}
  currentArrangement={arrangement}
  autoSync={true}
/>

// Manual sync
useEffect(() => {
  if (isPlaying) {
    osc.sendHardwareCommand('highlight_chord', { index: currentChordIndex });
  }
}, [isPlaying, currentChordIndex]);
```

### Multiple Controllers

```python
# Connect multiple controllers
manager.add_controller('push', push_controller)
manager.add_controller('launchpad', launchpad_controller)

# Use different controllers for different purposes
manager.set_active_controller('push')      # For composition
manager.set_active_controller('launchpad')  # For performance
```

---

## 🐛 Troubleshooting

### Controller Not Detected

```bash
# Check MIDI ports
python -c "import mido; print(mido.get_input_names())"

# Expected output:
# ['Ableton Push 2 User Port', 'Launchpad Pro Standalone Port', ...]
```

### Connection Fails

1. **Close other apps** using the controller
2. **Reconnect USB** cable
3. **Check mode:** 
   - Push: User Mode (auto-set)
   - Launchpad: Programmer Mode (auto-set)

### Pads Not Lighting

```python
# Manual test
controller.set_pad_color(0, (127, 0, 0))  # Should light first pad red
controller.clear_all_pads()                # Should turn off all pads
```

---

## 💡 Pro Tips

### Composition Workflow

1. **Use Chord Mode** for writing progressions
2. **AI suggests next chords** → displays on pads
3. **Press pads** to select chords (coming soon)
4. **See variations** in rows 3-6
5. **Switch to Section Mode** to arrange song structure

### Performance Workflow

1. **Pre-load arrangement** in Section Mode
2. **Each pad triggers** a section
3. **Use Scale Mode** for improvisation
4. **Color feedback** shows what's playing

### Learning Workflow

1. **Load a scale** in Scale Mode
2. **See highlighted notes** = in-scale
3. **Dim notes** = chromatic passing tones
4. **Experiment** with chord voicings in Chord Mode

---

## 📚 Further Reading

- [Full Hardware Guide](./HARDWARE_CONTROLLER_GUIDE.md)
- [OSC API Reference](./HARDWARE_CONTROLLER_GUIDE.md#api-reference)
- [Development Guide](../DEVELOPMENT_GUIDE.md)

---

## 🎵 Example: Complete Workflow

```javascript
// 1. Connect controller
await osc.sendHardwareCommand('connect', {
  type: 'push2',
  midiIn: 'Ableton Push 2 User Port',
  midiOut: 'Ableton Push 2 User Port'
});

// 2. Create progression with AI
const aiChords = await ai.generateFromNaturalLanguage(
  "create a chill lo-fi progression in C major"
);

// 3. Display on hardware
await osc.sendHardwareCommand('set_mode', { mode: 'chord' });
await osc.sendHardwareCommand('display_progression', { chords: aiChords });

// 4. Navigate and refine
for (let i = 0; i < aiChords.length; i++) {
  await osc.sendHardwareCommand('highlight_chord', { index: i });
  await sleep(2000); // Listen to each chord
}

// 5. Build arrangement
const arrangement = {
  sections: [
    { name: 'Intro', chords: aiChords.slice(0, 2) },
    { name: 'Verse', chords: aiChords },
    { name: 'Chorus', chords: chorusChords }
  ]
};

// 6. Display arrangement
await osc.sendHardwareCommand('set_mode', { mode: 'section' });
await osc.sendHardwareCommand('display_arrangement', arrangement);

// 7. Send to Live
await liveIntegration.createScenes(arrangement);
```

**Result:** Complete composition visualized on hardware, ready to record in Live! 🎉
