import os
import time
from pythonosc.udp_client import SimpleUDPClient

IP = os.getenv("ARRANGER_OSC_IP", "127.0.0.1")
PORT = int(os.getenv("ARRANGER_OSC_PORT", "12000"))

client = SimpleUDPClient(IP, PORT)

print(f"Sending OSC to {IP}:{PORT}")

# Transport
client.send_message("/live/set_tempo", 122.5)
client.send_message("/live/play", [])

# Scene
client.send_message("/live/create_scene_index", -1)
client.send_message("/live/trigger_scene", 0)

# Clip: create and add a Cmaj7 chord as four notes
client.send_message("/live/clip/create", [0, 0, 4.0])
for pitch in [60, 64, 67, 71]:
    client.send_message("/live/clip/add_note", [0, 0, pitch, 0.0, 1.0, 96])

# Track params
client.send_message("/live/track/set/volume", [0, 0.85])
client.send_message("/live/track/set/pan", [0, -0.2])

# Stop after a moment
time.sleep(0.5)
client.send_message("/live/stop", [])
print("Demo messages sent. Check server logs for replies.")
