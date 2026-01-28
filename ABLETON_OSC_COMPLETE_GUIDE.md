# AbletonOSC Complete Guide: Ins and Outs

## Overview

AbletonOSC is a MIDI Remote Script that exposes Ableton Live's entire API via Open Sound Control (OSC), allowing external applications to control Live programmatically.

## Architecture

```
Your Application (Python/Node/etc)
         ↓ OSC Messages
    Port 11000 (UDP)
         ↓
AbletonOSC Script (in Live)
         ↓
Live Object Model API
         ↓
Ableton Live
```

## Ports: Ins and Outs

### Input Port (Receiving Commands)
- **Port**: `11000`
- **Direction**: **IN** to AbletonOSC
- **Purpose**: Your application sends commands here
- **Protocol**: UDP
- **IP**: `127.0.0.1` (localhost) or your machine's IP

**Example**:
```python
from pythonosc import udp_client
client = udp_client.SimpleUDPClient("127.0.0.1", 11000)
client.send_message("/live/song/start_playing", [])
```

### Output Port (Receiving Replies)
- **Port**: `11001`
- **Direction**: **OUT** from AbletonOSC
- **Purpose**: AbletonOSC sends replies/responses here
- **Protocol**: UDP
- **IP**: Replies sent to the IP that sent the original message

**Example**:
```python
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

def handle_reply(address, *args):
    print(f"Received: {address} {args}")

dispatcher = Dispatcher()
dispatcher.map("/live/song/get/tempo", handle_reply)

server = BlockingOSCUDPServer(("127.0.0.1", 11001), dispatcher)
server.serve_forever()
```

## Communication Flow

### 1. One-Way Commands (No Reply Needed)

**Send command** → AbletonOSC executes → Done

```python
# Start playback (no reply needed)
client.send_message("/live/song/start_playing", [])

# Set tempo (no reply needed)
client.send_message("/live/song/set/tempo", [120.0])

# Create clip (no reply needed)
client.send_message("/live/clip_slot/create_clip", [0, 0, 4.0])
```

### 2. Query Commands (Reply Expected)

**Send query** → AbletonOSC processes → **Reply sent to port 11001**

```python
# Query tempo (reply comes to port 11001)
client.send_message("/live/song/get/tempo", [])

# You need a listener on port 11001 to receive:
# /live/song/get/tempo 120.0
```

### 3. Listeners (Automatic Updates)

**Start listener** → AbletonOSC sends updates automatically → **Updates to port 11001**

```python
# Start listening for tempo changes
client.send_message("/live/song/start_listen/tempo", [])

# Now AbletonOSC will send tempo updates to port 11001 whenever tempo changes
# /live/song/get/tempo 125.0
# /live/song/get/tempo 130.0
# etc.
```

## Key OSC Address Patterns

### Song Control
```
/live/song/start_playing          # Start playback
/live/song/stop_playing            # Stop playback
/live/song/set/tempo <bpm>        # Set tempo
/live/song/get/tempo               # Get tempo (reply to 11001)
/live/song/stop_all_clips          # Stop all clips
```

### Track Control
```
/live/track/set/volume <track> <volume>     # 0.0-1.0
/live/track/set/mute <track> <0|1>          # 0=unmuted, 1=muted
/live/track/set/solo <track> <0|1>          # 0=not solo, 1=solo
/live/track/set/arm <track> <0|1>           # 0=not armed, 1=armed
/live/track/get/name <track>                # Get track name (reply to 11001)
```

### Clip Control
```
/live/clip_slot/create_clip <track> <clip> <length>    # Create MIDI clip
/live/clip_slot/fire <track> <clip>                    # Fire clip
/live/clip/add/notes <track> <clip> <pitch> <start> <duration> <velocity> <mute>
/live/clip/remove/notes <track> <clip>                 # Remove all notes
/live/clip/get/notes <track> <clip>                    # Get notes (reply to 11001)
```

### Scene Control
```
/live/scene/fire <scene_index>                        # Fire scene
/live/scene/set/name <scene_index> <name>              # Set scene name
/live/song/create_scene <index>                        # Create scene (-1 = end)
```

## Message Format

### OSC Address Pattern
- Format: `/live/<object>/<action>/<property>`
- Examples:
  - `/live/song/start_playing`
  - `/live/track/set/volume`
  - `/live/clip/add/notes`

### Parameters
- **Types**: int, float, string
- **Order matters**: Parameters must match expected order
- **Arrays**: Some commands take multiple parameters

**Example**:
```python
# Add MIDI note: track, clip, pitch, start, duration, velocity, mute
client.send_message("/live/clip/add/notes", [
    0,      # track index
    0,      # clip index
    60,     # MIDI pitch (C4)
    0.0,    # start time (beats)
    1.0,    # duration (beats)
    100,    # velocity (0-127)
    0       # mute (0=not muted, 1=muted)
])
```

## Complete Example: Bidirectional Communication

```python
from pythonosc import udp_client
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import threading

# Client to send commands (port 11000)
client = udp_client.SimpleUDPClient("127.0.0.1", 11000)

# Dispatcher to handle replies (port 11001)
dispatcher = Dispatcher()

def handle_tempo(address, *args):
    print(f"Tempo: {args[0]} BPM")

def handle_beat(address, *args):
    print(f"Beat: {args[0]}")

# Map reply addresses
dispatcher.map("/live/song/get/tempo", handle_tempo)
dispatcher.map("/live/song/get/beat", handle_beat)

# Server to receive replies (port 11001)
server = BlockingOSCUDPServer(("127.0.0.1", 11001), dispatcher)

# Start server in background thread
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

# Now send commands and receive replies
print("Querying tempo...")
client.send_message("/live/song/get/tempo", [])

# Start listening for beats
print("Starting beat listener...")
client.send_message("/live/song/start_listen/beat", [])

# Set tempo
print("Setting tempo to 120 BPM...")
client.send_message("/live/song/set/tempo", [120.0])

# Keep running to receive updates
import time
time.sleep(10)
```

## Common Patterns

### Pattern 1: Fire and Forget
```python
# Just send command, don't wait for reply
client.send_message("/live/song/start_playing", [])
```

### Pattern 2: Query and Wait
```python
# Send query, wait for reply on port 11001
client.send_message("/live/song/get/tempo", [])
# Reply will come to your listener on port 11001
```

### Pattern 3: Continuous Monitoring
```python
# Start listener for property changes
client.send_message("/live/song/start_listen/tempo", [])

# Now updates come automatically to port 11001
# Stop listening when done:
client.send_message("/live/song/stop_listen/tempo", [])
```

## Error Handling

### Connection Errors
- **Port 11000 not responding**: AbletonOSC not running or not enabled
- **Check**: Look for "AbletonOSC: Listening for OSC on port 11000" in Live

### Invalid Commands
- **Wrong parameters**: Check parameter count and types
- **Invalid address**: Verify OSC address pattern
- **Errors sent to**: `/live/error` on port 11001

### Timeout Issues
- **Replies not received**: Make sure listener is running on port 11001
- **Network issues**: Check firewall settings

## Best Practices

1. **Always use port 11000 for sending**
2. **Always listen on port 11001 for replies**
3. **Handle errors**: Listen for `/live/error` messages
4. **Use listeners**: For real-time updates instead of polling
5. **Test connection**: Send `/live/test` first to verify

## Port Summary Table

| Port | Direction | Purpose | Who Uses It |
|------|-----------|---------|-------------|
| 11000 | **IN** | Receive commands | AbletonOSC listens here |
| 11001 | **OUT** | Send replies | AbletonOSC sends here |
| 12000 | IN | Arranger server | Your app (if using arranger) |
| 12001 | OUT | Arranger replies | Your app (if using arranger) |

## Quick Reference

### Send Commands (Port 11000)
```python
client = udp_client.SimpleUDPClient("127.0.0.1", 11000)
client.send_message("/live/song/start_playing", [])
```

### Receive Replies (Port 11001)
```python
server = BlockingOSCUDPServer(("127.0.0.1", 11001), dispatcher)
server.serve_forever()
```

### Test Connection
```python
client.send_message("/live/test", [])
# Should see confirmation in Live
```

## Integration with ChoCo

For sending ChoCo chord progressions:

```python
from pythonosc import udp_client
from choco_integration import harte_to_midi_notes

client = udp_client.SimpleUDPClient("127.0.0.1", 11000)

# Create clip
client.send_message("/live/clip_slot/create_clip", [0, 0, 32.0])

# Add chord notes
chord = "C:maj7"
midi_notes = harte_to_midi_notes(chord)  # [48, 52, 55, 59]

for note in midi_notes:
    client.send_message("/live/clip/add/notes", [
        0,      # track
        0,      # clip
        note,   # pitch
        0.0,    # start (beats)
        2.0,    # duration (beats)
        100,    # velocity
        0       # mute
    ])

# Fire clip
client.send_message("/live/clip_slot/fire", [0, 0])
```

## Troubleshooting

### "Connection refused"
- AbletonOSC not enabled in Live Preferences
- Port 11000 blocked by firewall
- Live not running

### "No reply received"
- Not listening on port 11001
- Wrong IP address
- Network configuration issue

### "Invalid OSC address"
- Check address pattern spelling
- Verify parameter count matches expected
- Check Live Object Model documentation
