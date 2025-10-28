# Max for Live (M4L) Quick Start Guide

Welcome to Max Live IDE! This guide will help you get started with Max for Live development using the AI-powered IDE.

## Getting Started with the AI Assistant

Click the **robot icon** 🤖 in the top toolbar to open the AI Assistant. The AI can help you with:

- **Understanding M4L concepts** - Ask about objects, patching techniques, etc.
- **Generating JavaScript code** - Describe what you want to create
- **Debugging patches** - Get help troubleshooting issues
- **Learning by example** - See code for common patterns

### Example Questions to Ask:

```
"How do I receive MIDI notes?"
"Create an arpeggiator"
"How do I control Live parameters?"
"Show me a simple MIDI effect"
"What's the difference between js and jsui?"
```

## Essential Max Objects for M4L

### MIDI Input/Output
- `notein` - Receive MIDI notes (pitch, velocity, channel)
- `noteout` - Send MIDI notes
- `ctlin` - Receive MIDI CC messages
- `ctlout` - Send MIDI CC messages
- `midiin` - Receive raw MIDI bytes
- `midiout` - Send raw MIDI bytes

### Live API Objects
- `live.path` - Navigate Live's object hierarchy
- `live.object` - Get/set Live object properties
- `live.observer` - Monitor Live property changes
- `live.dial` - Rotary control with Live integration
- `live.slider` - Slider with Live integration
- `live.toggle` - Toggle button

### JavaScript Objects
- `js` - Execute JavaScript code
- `jsui` - Custom UI with JavaScript + graphics

### Utility Objects
- `gate` - Route messages to different outlets
- `route` - Route messages by first element
- `select` - Compare and filter values
- `metro` - Metronome/clock generator
- `delay` - Delay messages by milliseconds

## Common Patterns

### 1. Simple MIDI Effect

```
notein → [your processing] → noteout
```

Example: Transpose all notes up 7 semitones
```
notein
   |
   + 7 (add 7 to pitch)
   |
noteout
```

### 2. Live API Integration

```
live.path "live_set tempo"
   |
live.object
   |
get/set messages
```

### 3. JavaScript Processing

Create a `js` object and click it to open the code editor. The AI can generate code for you!

Basic structure:
```javascript
inlets = 1;
outlets = 1;

function msg_int(v) {
    // Process integer input
    outlet(0, v * 2);
}
```

## Keyboard Shortcuts

- `Cmd/Ctrl + F` - Search for devices
- `Cmd/Ctrl + Shift + O` - Open Object Browser
- `Cmd/Ctrl + =` - Zoom in
- `Cmd/Ctrl + -` - Zoom out
- `Cmd/Ctrl + R` - Reset zoom
- `Esc` - Close panels

## Using the AI Assistant Effectively

### 1. Be Specific
❌ "Make a MIDI thing"
✅ "Create a MIDI arpeggiator that plays notes in ascending order"

### 2. Ask for Explanations
"Explain what the live.path object does"
"How does message routing work in Max?"

### 3. Request Code
"Generate JavaScript code for a scale quantizer"
"Show me how to create a note delay effect"

### 4. Debug Together
"This code isn't working: [paste code]"
"How do I fix stuck MIDI notes?"

## Quick Tutorial: Your First MIDI Effect

Let's create a simple note transposer:

1. **Ask the AI**: "Show me how to create a MIDI transposer"

2. The AI will guide you to create:
   - `notein` object (receives MIDI)
   - `+ 7` object (adds 7 semitones)
   - `noteout` object (sends MIDI)

3. Connect them: `notein` → `+` → `noteout`

4. Test it in Live!

## JavaScript Quick Reference

### Max JS Essentials

```javascript
// Declare inlets and outlets
inlets = 2;
outlets = 1;

// Handle integer input
function msg_int(v) {
    outlet(0, v);
}

// Handle float input
function msg_float(v) {
    outlet(0, v);
}

// Handle lists
function list() {
    var args = arrayfromargs(arguments);
    outlet(0, args);
}

// Handle bang
function bang() {
    post("Bang received!\\n");
}

// Check which inlet received data
if (inlet === 0) {
    // Data from inlet 0
}
```

### Common Patterns

**MIDI Note Processing:**
```javascript
function list() {
    var pitch = arguments[0];
    var velocity = arguments[1];
    
    // Your processing here
    
    outlet(0, [pitch, velocity]);
}
```

**Scale Quantization:**
```javascript
var scale = [0, 2, 4, 5, 7, 9, 11]; // Major scale

function quantize(note) {
    var pitchClass = note % 12;
    var octave = Math.floor(note / 12);
    
    // Find nearest scale note
    var closest = scale[0];
    var minDist = Math.abs(pitchClass - closest);
    
    for (var i = 1; i < scale.length; i++) {
        var dist = Math.abs(pitchClass - scale[i]);
        if (dist < minDist) {
            minDist = dist;
            closest = scale[i];
        }
    }
    
    return (octave * 12) + closest;
}
```

## Live API Examples

### Get Current Tempo
```
live.path "live_set tempo"
   |
live.object
   |
get (send 'get' message)
```

### Control Track Volume
```
live.path "live_set tracks 0 mixer_device volume"
   |
live.object
   |
[number] (set volume 0-1)
```

### Monitor Selected Track
```
live.path "live_set view selected_track"
   |
live.observer
   |
(outputs track ID when selection changes)
```

## Tips for Success

1. **Start Simple** - Begin with basic MIDI processing before complex effects
2. **Use the AI** - Don't hesitate to ask questions or request code generation
3. **Test Incrementally** - Build and test small parts before combining them
4. **Save Often** - Save your patches frequently
5. **Learn by Example** - Ask the AI to show you examples of what you want to create

## Common Questions

**Q: How do I know which object to use?**  
A: Ask the AI! Type "What object should I use to..." and describe your goal.

**Q: My MIDI notes are stuck**  
A: Add a `flush` object to clear stuck notes, or ask the AI for help debugging.

**Q: How do I make a custom UI?**  
A: Use `jsui` for completely custom graphics, or `live.*` objects for standard controls.

**Q: Can I use external libraries?**  
A: JavaScript in Max has some limitations, but ask the AI about specific needs.

## Next Steps

1. **Try the AI Chat** - Click the robot icon and ask for help
2. **Explore Objects** - Use Cmd+Shift+O to browse available objects
3. **Generate Code** - Click on any `js` object to open the AI-powered editor
4. **Build Something** - Start with a simple MIDI effect and expand from there

## Resources

- Max 8 Documentation: https://docs.cycling74.com/
- Max for Live Essentials: https://help.ableton.com/hc/en-us/articles/212086305
- JavaScript in Max: https://docs.cycling74.com/max8/vignettes/jsprogrammingintro

---

**Need Help?** Click the 🤖 robot icon and ask the AI assistant anything!
