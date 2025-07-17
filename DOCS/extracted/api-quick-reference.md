# Ableton Live Development Quick Reference

## Common LOM Paths

### Tracks
`javascript
"live_set tracks 0"                    // First track
"live_set tracks 0 name"               // Track name  
"live_set tracks 0 mute"               // Track mute state
"live_set tracks 0 solo"               // Track solo state
"live_set tracks 0 volume"             // Track volume
`

### Devices
`javascript
"live_set tracks 0 devices 0"          // First device on first track
"live_set tracks 0 devices 0 name"     // Device name
"live_set tracks 0 devices 0 parameters 0"        // First parameter
"live_set tracks 0 devices 0 parameters 0 value"  // Parameter value
`

### Clips
`javascript
"live_set tracks 0 clip_slots 0"       // First clip slot
"live_set tracks 0 clip_slots 0 clip"  // Clip in slot
"live_set tracks 0 clip_slots 0 has_clip"  // Slot has clip
`

### Transport
`javascript
"live_set tempo"                       // Current tempo
"live_set is_playing"                  // Transport playing
"live_set metronome"                   // Metronome on/off
`

## JavaScript Patterns

### Basic LiveAPI Setup
`javascript
// Create LiveAPI object
var api = new LiveAPI("live_set");

// With callback
var api = new LiveAPI(callback, "live_set tracks 0");
function callback() {
    post("LiveAPI callback triggered");
}
`

### Parameter Control
`javascript
// Get parameter value
var param = new LiveAPI("live_set tracks 0 devices 0 parameters 0");
var value = param.get("value")[0];

// Set parameter value
param.set("value", [0.5]);

// Observe parameter changes
param.property = "value";
function paramChanged() {
    var newValue = param.get("value")[0];
    outlet(0, newValue);
}
`

### Track Control
`javascript
// Mute/unmute track
var track = new LiveAPI("live_set tracks 0");
track.set("mute", [1]); // Mute
track.set("mute", [0]); // Unmute

// Solo track
track.set("solo", [1]);

// Set track volume (0.0 - 1.0)
track.set("volume", [0.8]);
`

### Clip Launch
`javascript
// Launch clip
var clip = new LiveAPI("live_set tracks 0 clip_slots 0");
clip.call("fire");

// Stop clip
clip.call("stop");

// Check if slot has clip
var hasClip = clip.get("has_clip")[0];
`

## Max for Live Device Template

### Basic Device Structure
`javascript
outlets = 2;
var liveAPI;

function loadbang() {
    liveAPI = new LiveAPI("this_device");
    post("Device loaded");
}

function bang() {
    // Trigger device action
    outlet(0, "bang");
}

function anything() {
    var args = arrayfromargs(arguments);
    var message = args[0];
    var value = args[1];
    
    // Handle incoming messages
    switch(message) {
        case "param":
            setParameter(value);
            break;
        default:
            post("Unknown message: " + message);
    }
}

function setParameter(value) {
    if (liveAPI) {
        liveAPI.set("parameters 0 value", [value]);
    }
}
`

### Parameter Mapping
`javascript
// Map inlet to device parameter
function mapToParameter(trackIndex, deviceIndex, paramIndex) {
    return function(value) {
        var path = "live_set tracks " + trackIndex + 
                  " devices " + deviceIndex + 
                  " parameters " + paramIndex;
        var api = new LiveAPI(path);
        api.set("value", [value]);
    };
}

// Usage
var mapParam1 = mapToParameter(0, 0, 0);
mapParam1(0.5); // Set parameter to 0.5
`

## Common Device Types

### Audio Effects
- "Reverb" - Ableton Reverb
- "Delay" - Ableton Delay  
- "Eq8" - EQ Eight
- "Compressor2" - Compressor
- "Saturator" - Saturator

### MIDI Effects
- "Arpeggiator" - Arpeggiator
- "Scale" - Scale effect
- "Chord" - Chord effect
- "NoteLength" - Note Length

### Instruments
- "Wavetable" - Wavetable synth
- "Operator" - Operator FM synth
- "Simpler" - Simpler sampler
- "DrumRack" - Drum Rack

## Error Handling

### Safe LiveAPI Access
`javascript
function safeGetValue(path) {
    try {
        var api = new LiveAPI(path);
        if (api.id != 0) {
            return api.get("value")[0];
        }
    } catch(e) {
        error("LiveAPI error: " + e.message);
    }
    return null;
}

function safeSetValue(path, value) {
    try {
        var api = new LiveAPI(path);
        if (api.id != 0) {
            api.set("value", [value]);
            return true;
        }
    } catch(e) {
        error("LiveAPI error: " + e.message);
    }
    return false;
}
`

## MIDI Integration

### Note Input/Output
`javascript
// Handle MIDI input
function notein(pitch, velocity, channel) {
    if (velocity > 0) {
        // Note on
        outlet(0, pitch, velocity);
    } else {
        // Note off  
        outlet(1, pitch, 0);
    }
}

// Send MIDI output
function sendNote(pitch, velocity, channel) {
    outlet(0, "note", pitch, velocity, channel);
}
`

### Control Change
`javascript
// Handle CC input
function ctlin(controller, value, channel) {
    var normalized = value / 127.0;
    
    // Map to parameter
    var paramPath = "live_set tracks 0 devices 0 parameters " + controller;
    var api = new LiveAPI(paramPath);
    api.set("value", [normalized]);
}

// Send CC output
function sendCC(controller, value, channel) {
    outlet(0, "cc", controller, value, channel);
}
`

## Utility Functions

### Array Helpers
`javascript
// Convert arguments to array
function argsToArray() {
    return Array.prototype.slice.call(arguments);
}

// Map value from one range to another
function mapRange(value, inMin, inMax, outMin, outMax) {
    return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
}

// Clamp value to range
function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}
`

### Device Discovery
`javascript
function findDevice(trackIndex, deviceName) {
    var trackPath = "live_set tracks " + trackIndex;
    var track = new LiveAPI(trackPath);
    var deviceCount = track.get("devices").length;
    
    for (var i = 0; i < deviceCount; i++) {
        var devicePath = trackPath + " devices " + i;
        var device = new LiveAPI(devicePath);
        var name = device.get("name")[0];
        
        if (name === deviceName) {
            return i;
        }
    }
    return -1;
}
`

## Performance Tips

1. **Cache LiveAPI objects** for frequently accessed paths
2. **Minimize observer callbacks** in audio-rate processes  
3. **Batch parameter updates** when possible
4. **Use setTimeout** for deferred processing
5. **Avoid creating LiveAPI objects** in tight loops

## Common Gotchas

- LiveAPI paths use spaces, not dots or slashes
- Array indices are 0-based
- Some Live API calls return arrays even for single values
- Device loading is asynchronous
- Parameter ranges may vary between device types
- Track indices change when tracks are reordered

---
*Quick reference for Ableton Live API development*
