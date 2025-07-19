# Node for Max API Reference

## Overview
Node for Max enables JavaScript/Node.js development within Max for Live, providing access to npm packages and modern JavaScript features.

## Installation & Setup

### Requirements
- Max for Live
- Node.js installed on system
- Node for Max package from Max Package Manager

### Basic Setup
1. Install Node for Max from Package Manager
2. Add 
ode.script object to Max patch
3. Configure Node.js script path
4. Enable Node for Max in Max preferences

## Core Objects

### node.script
Main object for running Node.js scripts in Max.

`javascript
// Basic node.script setup
const { MaxAPI } = require("max-api");

// Initialize
MaxAPI.post("Node for Max script loaded");

// Handle messages from Max
MaxAPI.addHandler("message_name", (arg1, arg2) => {
    MaxAPI.post(Received: , );
});

// Send to Max outlet
MaxAPI.outlet(["data", "to", "max"]);
`

### node.script.view
Node.js script with visual interface.

## Max API Interface

### Core Functions

#### Communication
`javascript
// Send data to Max outlets
MaxAPI.outlet(data);           // To outlet 0
MaxAPI.outlet(data, 1);        // To specific outlet

// Post to Max console
MaxAPI.post("Message");
MaxAPI.error("Error message");

// Get Max environment info
const maxVersion = MaxAPI.getMaxVersion();
const nodeVersion = process.version;
`

#### Message Handlers
`javascript
// Register message handler
MaxAPI.addHandler("my_message", (value) => {
    // Handle incoming message from Max
    MaxAPI.post(Received value: );
});

// Handle multiple arguments
MaxAPI.addHandler("multi_arg", (...args) => {
    MaxAPI.post(Arguments: );
});

// Remove handler
MaxAPI.removeHandler("my_message");
`

#### Async Operations
`javascript
// Async handler
MaxAPI.addHandler("async_task", async (url) => {
    try {
        const response = await fetch(url);
        const data = await response.json();
        MaxAPI.outlet(["success", data]);
    } catch (error) {
        MaxAPI.outlet(["error", error.message]);
    }
});
`

## npm Package Integration

### Installation
`ash
# In your Node for Max script directory
npm init -y
npm install package-name
`

### Common Packages
`javascript
// File system operations
const fs = require("fs");
const path = require("path");

// HTTP requests  
const axios = require("axios");
const fetch = require("node-fetch");

// Audio processing
const wavefile = require("wavefile");
const audiobuffer = require("audiobuffer");

// MIDI processing
const midi = require("midi");
const jsmidgen = require("jsmidgen");

// Machine Learning
const ml = require("ml-matrix");
const tensorflow = require("@tensorflow/tfjs-node");
`

## Live API Integration

### Accessing Live Object Model
`javascript
const { MaxAPI } = require("max-api");

// Create LiveAPI instance through Max
MaxAPI.addHandler("get_track_name", (trackIndex) => {
    // Send LiveAPI command to Max
    MaxAPI.outlet(["liveapi", "live_set", "tracks", trackIndex, "name"]);
});

// Receive LiveAPI response
MaxAPI.addHandler("liveapi_response", (value) => {
    MaxAPI.post(Track name: );
});
`

### Parameter Control
`javascript
// Set device parameter
function setParameter(trackIndex, deviceIndex, paramIndex, value) {
    const path = live_set tracks  devices  parameters ;
    MaxAPI.outlet(["liveapi_set", path, "value", value]);
}

// Get parameter value
function getParameter(trackIndex, deviceIndex, paramIndex) {
    const path = live_set tracks  devices  parameters ;
    MaxAPI.outlet(["liveapi_get", path, "value"]);
}
`

## Audio Processing

### Buffer Manipulation
`javascript
const fs = require("fs");
const WaveFile = require("wavefile").WaveFile;

MaxAPI.addHandler("process_audio", async (filePath) => {
    try {
        // Read audio file
        const buffer = fs.readFileSync(filePath);
        const wav = new WaveFile(buffer);
        
        // Process samples
        const samples = wav.getSamples();
        const processed = samples.map(sample => sample * 0.5); // Gain reduction
        
        // Create new wav
        wav.fromScratch(1, 44100, "32f", processed);
        
        // Save processed audio
        const outputPath = filePath.replace(".wav", "_processed.wav");
        fs.writeFileSync(outputPath, wav.toBuffer());
        
        MaxAPI.outlet(["audio_processed", outputPath]);
    } catch (error) {
        MaxAPI.error(Audio processing error: );
    }
});
`

## MIDI Processing

### MIDI File Generation
`javascript
const Midi = require("jsmidgen");

MaxAPI.addHandler("generate_midi", (notes) => {
    const track = new Midi.Track();
    
    notes.forEach((note, index) => {
        track.addNote(0, note.pitch, note.duration, note.time);
    });
    
    const song = new Midi.File();
    song.addTrack(track);
    
    const buffer = song.toBytes();
    const filePath = "generated_midi.mid";
    
    fs.writeFileSync(filePath, Buffer.from(buffer));
    MaxAPI.outlet(["midi_generated", filePath]);
});
`

## File System Operations

### File Watching
`javascript
const chokidar = require("chokidar");

MaxAPI.addHandler("watch_folder", (folderPath) => {
    const watcher = chokidar.watch(folderPath);
    
    watcher.on("add", (path) => {
        MaxAPI.outlet(["file_added", path]);
    });
    
    watcher.on("change", (path) => {
        MaxAPI.outlet(["file_changed", path]);
    });
});
`

### JSON Configuration
`javascript
const config = require("./config.json");

MaxAPI.addHandler("save_config", (settings) => {
    const configPath = "./config.json";
    fs.writeFileSync(configPath, JSON.stringify(settings, null, 2));
    MaxAPI.outlet(["config_saved"]);
});

MaxAPI.addHandler("load_config", () => {
    MaxAPI.outlet(["config_loaded", config]);
});
`

## Error Handling

### Robust Error Management
`javascript
// Global error handling
process.on("uncaughtException", (error) => {
    MaxAPI.error(Uncaught exception: );
});

process.on("unhandledRejection", (reason, promise) => {
    MaxAPI.error(Unhandled rejection: );
});

// Wrapped handlers
function safeHandler(name, handler) {
    MaxAPI.addHandler(name, async (...args) => {
        try {
            await handler(...args);
        } catch (error) {
            MaxAPI.error(Handler  error: );
        }
    });
}
`

## Performance Optimization

### Best Practices
1. **Minimize MaxAPI calls** in tight loops
2. **Cache frequently accessed data**
3. **Use async/await** for I/O operations
4. **Implement proper cleanup** on script shutdown
5. **Batch Live API operations**

### Memory Management
`javascript
// Cleanup on shutdown
MaxAPI.addHandler(MaxAPI.MESSAGE_TYPES.SHUTDOWN, () => {
    // Close file handles
    // Clear intervals/timeouts
    // Disconnect from external services
    MaxAPI.post("Node script shutting down");
});
`

## Common Patterns

### Device Controller
`javascript
class DeviceController {
    constructor(trackIndex, deviceIndex) {
        this.trackIndex = trackIndex;
        this.deviceIndex = deviceIndex;
        this.basePath = live_set tracks  devices ;
    }
    
    setParameter(paramIndex, value) {
        MaxAPI.outlet(["liveapi_set", this.basePath, "parameters", paramIndex, "value", value]);
    }
    
    getParameter(paramIndex) {
        MaxAPI.outlet(["liveapi_get", this.basePath, "parameters", paramIndex, "value"]);
    }
}
`

### State Manager
`javascript
class StateManager {
    constructor() {
        this.state = {};
        this.subscribers = [];
    }
    
    setState(key, value) {
        this.state[key] = value;
        this.notifySubscribers(key, value);
    }
    
    subscribe(callback) {
        this.subscribers.push(callback);
    }
    
    notifySubscribers(key, value) {
        this.subscribers.forEach(callback => callback(key, value));
    }
}
`

---
*Extracted from Max 9 Node for Max API Documentation*
