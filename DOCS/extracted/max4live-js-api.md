# Max for Live JavaScript API Reference

## Overview
This document contains essential JavaScript API information extracted from the official Max 9 JavaScript API documentation.

## Core JavaScript Objects in Max for Live

### Global Objects
- max - Main Max interface object
- outlet() - Send data from outlet
- post() - Print to Max console
- rror() - Print error message

### Live Object Model (LOM) Access
`javascript
// Get Live application
var live = new LiveAPI();

// Access current Live set
live.path = "live_set";

// Get tracks
live.path = "live_set tracks 0"; // First track

// Get devices
live.path = "live_set tracks 0 devices 0"; // First device on first track
`

### Device Parameter Control
`javascript
// Create Live API object
var liveObject = new LiveAPI("live_set tracks 0 devices 0 parameters 0");

// Get parameter value
var value = liveObject.get("value");

// Set parameter value
liveObject.set("value", [0.5]);

// Observe parameter changes
liveObject.property = "value";
function valueChanged() {
    post("Parameter changed to: " + liveObject.get("value"));
}
`

### MIDI Integration
`javascript
// MIDI input handling
function notein(pitch, velocity, channel) {
    // Handle MIDI note input
    outlet(0, pitch, velocity);
}

// Control change handling  
function ctlin(controller, value, channel) {
    // Handle MIDI CC input
    var normalizedValue = value / 127.0;
    outlet(1, normalizedValue);
}
`

### Audio Signal Processing
`javascript
// Audio processing in gen~ codebox
function process(input) {
    // Process audio sample
    var output = input * 0.5; // Simple gain
    return output;
}
`

## Common Patterns

### Device Initialization
`javascript
// Device setup
outlets = 2;
var liveAPI;

function loadbang() {
    liveAPI = new LiveAPI("this_device");
    post("Device loaded successfully");
}
`

### Parameter Mapping
`javascript
function mapParameter(parameterPath, minVal, maxVal) {
    var api = new LiveAPI(parameterPath);
    api.set("value", [map(arguments[3], 0, 1, minVal, maxVal)]);
}
`

## Error Handling
`javascript
try {
    var api = new LiveAPI("invalid_path");
} catch(e) {
    error("LiveAPI error: " + e.message);
}
`

## Best Practices
1. Always check if LiveAPI objects are valid before use
2. Use try-catch blocks for robust error handling
3. Observe parameter changes rather than polling
4. Minimize Live API calls in audio-rate processes
5. Cache frequently accessed Live objects

## Performance Tips
- Avoid creating new LiveAPI objects in audio callbacks
- Use object pooling for frequently accessed parameters
- Batch parameter updates when possible
- Use live.observer for efficient parameter monitoring

---
*Extracted from Max 9 JavaScript API Documentation*
