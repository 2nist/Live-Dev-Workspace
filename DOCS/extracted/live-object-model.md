# Live Object Model (LOM) Reference

## Overview
The Live Object Model provides hierarchical access to all elements in an Ableton Live set through a structured API.

## Core LOM Hierarchy

### Application Level
`
live_app/
├── live_set/           # Current Live set
├── control_surfaces/   # Connected controllers
└── browser/           # Live browser content
`

### Live Set Structure
`
live_set/
├── tracks/            # Audio, MIDI, and return tracks
├── scenes/            # Session view scenes  
├── master_track/      # Master track
├── return_tracks/     # Return tracks
├── visible_tracks/    # Currently visible tracks
├── tempo/             # Global tempo
├── signature/         # Time signature
└── is_playing/        # Transport state
`

## Track Objects

### Track Properties
- 
ame - Track name
- color - Track color (RGB)
- is_foldable - Can contain other tracks
- is_grouped - Is part of a group
- mute - Mute state
- solo - Solo state  
- rm - Record arm state
- olume - Track volume
- panning - Track pan

### Track Hierarchy
`
tracks N/
├── devices/           # Audio/MIDI devices
├── clip_slots/        # Session view clips
├── mixer_device/      # Track mixer
├── view/             # Track view state
└── canonical_parent/  # Parent group track
`

## Device Objects

### Device Properties
- 
ame - Device name
- class_name - Device type identifier
- is_active - Device on/off state
- presets - Available presets
- parameters - Device parameters

### Device Types
- **Audio Effects**: Reverb, Delay, EQ, etc.
- **MIDI Effects**: Arpeggiator, Scale, etc.  
- **Instruments**: Wavetable, Operator, etc.
- **Max for Live**: Custom M4L devices

## Parameter Objects

### Parameter Properties
- alue - Current parameter value (0.0 - 1.0)
- min - Minimum value
- max - Maximum value  
- 
ame - Parameter display name
- original_name - Internal parameter name
- is_quantized - Discrete vs continuous
- alue_items - Available discrete values

### Parameter Control
`javascript
// Direct value setting
parameter.set("value", [0.5]);

// Value mapping
var mappedValue = parameter.get("min")[0] + 
    (parameter.get("max")[0] - parameter.get("min")[0]) * normalizedValue;
`

## Clip Objects

### Clip Properties
- 
ame - Clip name
- length - Clip length in beats
- loop_start - Loop start position
- loop_end - Loop end position
- is_playing - Currently playing
- is_triggered - Triggered to play
- has_clip - Slot contains a clip

### Clip Manipulation
`javascript
// Launch clip
clip.call("fire");

// Stop clip  
clip.call("stop");

// Delete clip
clip.call("delete_clip");
`

## Scene Objects

### Scene Properties
- 
ame - Scene name
- color - Scene color
- is_triggered - Scene is triggered
- 	empo - Scene tempo (if different)

### Scene Control
`javascript
// Launch scene
scene.call("fire");

// Stop all clips in scene
scene.call("stop_all_clips");
`

## Common LOM Paths

### Navigation Examples
`javascript
// Get first track
"live_set tracks 0"

// Get first device on first track  
"live_set tracks 0 devices 0"

// Get first parameter of first device
"live_set tracks 0 devices 0 parameters 0"

// Get first clip slot on first track
"live_set tracks 0 clip_slots 0"

// Get master track volume
"live_set master_track mixer_device volume"

// Get tempo
"live_set tempo"

// Get time signature
"live_set signature numerator"
"live_set signature denominator"
`

### Dynamic Path Construction
`javascript
function getTrackDevice(trackIndex, deviceIndex) {
    return "live_set tracks " + trackIndex + " devices " + deviceIndex;
}

function getParameter(trackIndex, deviceIndex, paramIndex) {
    return getTrackDevice(trackIndex, deviceIndex) + " parameters " + paramIndex;
}
`

## Observer Patterns

### Parameter Observation
`javascript
var parameterAPI = new LiveAPI("live_set tracks 0 devices 0 parameters 0");
parameterAPI.property = "value";

function parameterChanged() {
    var newValue = parameterAPI.get("value")[0];
    post("Parameter changed to: " + newValue);
}
`

### Track State Observation
`javascript
var trackAPI = new LiveAPI("live_set tracks 0");
trackAPI.property = "mute";

function muteChanged() {
    var isMuted = trackAPI.get("mute")[0];
    post("Track mute: " + isMuted);
}
`

## Best Practices

1. **Path Validation**: Always verify paths exist before accessing
2. **Observer Cleanup**: Remove observers when no longer needed  
3. **Batch Operations**: Group multiple parameter changes
4. **Error Handling**: Wrap LOM access in try-catch blocks
5. **Performance**: Cache frequently accessed Live objects

## Common Gotchas

- Array indices are 0-based
- Some properties return arrays even for single values
- Device loading is asynchronous
- Parameter ranges may change between devices
- Track indices can change when tracks are added/removed

---
*Extracted from Max 9 Live Object Model Documentation*
