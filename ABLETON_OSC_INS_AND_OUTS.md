# AbletonOSC: Ins and Outs Explained

## Port Configuration

### Port 11000: INPUT (Commands IN to AbletonOSC)
- **Direction**: Your application → AbletonOSC
- **Purpose**: Send commands to control Ableton Live
- **Protocol**: UDP
- **IP**: `127.0.0.1` (localhost)

**What goes IN**:
- Play/stop commands
- Parameter changes (tempo, volume, etc.)
- Clip creation and manipulation
- Track control commands
- Scene triggers

**Example**:
```python
from pythonosc import udp_client
client = udp_client.SimpleUDPClient("127.0.0.1", 11000)

# Send command IN to AbletonOSC
client.send_message("/live/song/start_playing", [])
client.send_message("/live/song/set/tempo", [120.0])
client.send_message("/live/clip/add/notes", [0, 0, 60, 0.0, 1.0, 100, 0])
```

### Port 11001: OUTPUT (Replies OUT from AbletonOSC)
- **Direction**: AbletonOSC → Your application
- **Purpose**: Receive replies and status updates
- **Protocol**: UDP
- **IP**: Replies sent to the IP that sent the original message

**What comes OUT**:
- Query responses (tempo, track names, etc.)
- Status updates (when listening)
- Error messages
- Property change notifications

**Example**:
```python
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

def handle_reply(address, *args):
    print(f"Received from AbletonOSC: {address} = {args}")

dispatcher = Dispatcher()
dispatcher.map("/live/song/get/tempo", handle_reply)
dispatcher.map("/live/error", handle_reply)

# Listen for replies OUT from AbletonOSC
server = BlockingOSCUDPServer(("127.0.0.1", 11001), dispatcher)
server.serve_forever()
```

## Communication Patterns

### 1. One-Way Commands (No Reply)
```
Your App → Port 11000 → AbletonOSC → Live
(No response needed)
```

### 2. Query with Reply
```
Your App → Port 11000 → AbletonOSC → Live
                                    ↓
Your App ← Port 11001 ← AbletonOSC ← (query result)
```

### 3. Continuous Updates (Listeners)
```
Your App → Port 11000 → AbletonOSC (start listener)
                                    ↓
Your App ← Port 11001 ← AbletonOSC ← (continuous updates)
```

## Complete Bidirectional Example

```python
import threading
from pythonosc import udp_client
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

# OUT: Send commands to AbletonOSC (port 11000)
client = udp_client.SimpleUDPClient("127.0.0.1", 11000)

# IN: Receive replies from AbletonOSC (port 11001)
dispatcher = Dispatcher()

def handle_tempo(address, *args):
    print(f"Tempo update: {args[0]} BPM")

def handle_error(address, *args):
    print(f"Error: {args}")

dispatcher.map("/live/song/get/tempo", handle_tempo)
dispatcher.map("/live/error", handle_error)

server = BlockingOSCUDPServer(("127.0.0.1", 11001), dispatcher)

# Start server in background
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

# Now send commands and receive replies
client.send_message("/live/song/get/tempo", [])  # Query
client.send_message("/live/song/start_listen/tempo", [])  # Listen for changes
client.send_message("/live/song/set/tempo", [125.0])  # Change tempo
# Replies will come to port 11001 automatically
```

## Key Points

1. **Port 11000 = INPUT**: You send commands here
2. **Port 11001 = OUTPUT**: You receive replies here
3. **Always listen on 11001** if you need replies
4. **UDP protocol**: Fast but no guaranteed delivery
5. **Localhost only**: Default is 127.0.0.1 (can use network IP for remote)

## Common Mistakes

❌ **Sending to port 11001**: Won't work, that's for replies
✅ **Send to 11000**: Correct port for commands

❌ **Not listening on 11001**: Won't receive replies
✅ **Listen on 11001**: Required for queries and updates

❌ **Expecting immediate replies**: UDP is asynchronous
✅ **Use listeners**: For real-time updates

## Summary

- **IN (11000)**: Your commands go IN to AbletonOSC
- **OUT (11001)**: AbletonOSC replies come OUT to you
- **Bidirectional**: Use both ports for full control
- **Asynchronous**: Replies come when ready, not immediately
